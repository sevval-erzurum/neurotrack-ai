"""Doktor onayı, yönetici rolü ve erişim günlüğü."""

from tests.conftest import audit_events

DOCTOR = {"full_name": "Dr. Yeni", "password": "correct-horse-1", "role": "doctor"}


def _care_team_add(owner, subject_id: int, email: str):
    return owner.post(f"/subjects/{subject_id}/care-team", json={"email": email})


# --- Kayıt ----------------------------------------------------------------------


def test_doctor_registration_requires_license_and_institution(anon):
    response = anon.post("/auth/register", json=DOCTOR | {"email": "dr.eksik@example.com"})
    assert response.status_code == 422
    response = anon.post(
        "/auth/register",
        json=DOCTOR | {"email": "dr.eksik@example.com", "license_number": "TR-1234", "institution": "X Hastanesi"},
    )
    assert response.status_code == 201
    assert response.json()["doctor_status"] == "pending"


def test_admin_role_cannot_be_self_registered(anon):
    response = anon.post(
        "/auth/register",
        json={"full_name": "Sahte Yönetici", "email": "root@example.com", "password": "correct-horse-1", "role": "admin"},
    )
    assert response.status_code == 422


def test_new_doctor_application_notifies_admins(admin, make_user):
    make_user("doctor", email="dr.basvuru@example.com", approved=False)
    titles = [n["title"] for n in admin.get("/notifications").json()]
    assert "Yeni doktor başvurusu" in titles


# --- Onay akışı ------------------------------------------------------------------


def test_pending_doctor_cannot_be_added_until_approved(admin, make_user, parent_with_toddler):
    parent, child = parent_with_toddler
    doctor = make_user("doctor", email="dr.bekleyen@example.com", approved=False)

    response = _care_team_add(parent, child["id"], "dr.bekleyen@example.com")
    assert response.status_code == 404
    # Var olmayan bir e-postayla aynı yanıt: başvurunun varlığı sızmaz.
    assert response.json() == _care_team_add(parent, child["id"], "yok@example.com").json()

    assert admin.post(f"/admin/doctors/{doctor.user['id']}/approve", json={}).status_code == 200
    assert doctor.get("/auth/me").json()["doctor_status"] == "approved"
    assert _care_team_add(parent, child["id"], "dr.bekleyen@example.com").status_code == 201
    assert doctor.get(f"/subjects/{child['id']}").status_code == 200
    assert "Hesabınız onaylandı" in [n["title"] for n in doctor.get("/notifications").json()]


def test_suspension_revokes_access_immediately_and_reapproval_restores_it(admin, make_user, parent_with_toddler):
    parent, child = parent_with_toddler
    doctor = make_user("doctor", email="dr.askida@example.com")
    _care_team_add(parent, child["id"], "dr.askida@example.com")
    parent.post(f"/conversations/{doctor.user['id']}/messages", json={"body": "Merhaba"})
    base = f"/subjects/{child['id']}"

    response = admin.post(f"/admin/doctors/{doctor.user['id']}/suspend", json={"reason": "Lisans doğrulanamadı"})
    assert response.status_code == 200

    for path in ("", "/logs", "/screenings", "/notes", "/insights"):
        assert doctor.get(base + path).status_code == 404, path
    assert doctor.get("/subjects").json() == []
    assert doctor.post(f"{base}/notes", json={"body": "not"}).status_code == 404
    assert doctor.get("/conversations").json() == []
    assert doctor.post(f"/conversations/{parent.user['id']}/messages", json={"body": "x"}).status_code == 404
    assert parent.get("/conversations").json() == []
    # Veri sahibi doktorun durumunu görür; bakım ekibi kaydı silinmez.
    team = parent.get(base).json()["care_team"]
    assert [(d["email"], d["doctor_status"]) for d in team] == [("dr.askida@example.com", "suspended")]

    assert admin.post(f"/admin/doctors/{doctor.user['id']}/approve", json={}).status_code == 200
    assert doctor.get(base).status_code == 200


def test_review_transitions_are_validated(admin, make_user):
    pending = make_user("doctor", email="dr.gecis@example.com", approved=False)
    approved = make_user("doctor", email="dr.onayli@example.com")

    assert admin.post(f"/admin/doctors/{pending.user['id']}/reject", json={}).status_code == 422  # gerekçe zorunlu
    assert admin.post(f"/admin/doctors/{pending.user['id']}/suspend", json={"reason": "neden"}).status_code == 409
    assert admin.post(f"/admin/doctors/{approved.user['id']}/reject", json={"reason": "neden"}).status_code == 409
    rejected = admin.post(f"/admin/doctors/{pending.user['id']}/reject", json={"reason": "Belge eksik"})
    assert rejected.status_code == 200
    me = pending.get("/auth/me").json()
    assert (me["doctor_status"], me["status_reason"]) == ("rejected", "Belge eksik")


def test_admin_doctor_list_filters_by_status(admin, make_user):
    make_user("doctor", email="dr.a@example.com", approved=False)
    make_user("doctor", email="dr.b@example.com")
    pending = admin.get("/admin/doctors", params={"status": "pending"}).json()
    assert [d["email"] for d in pending] == ["dr.a@example.com"]
    assert pending[0]["license_number"] and pending[0]["institution"] == "Test Hastanesi"
    assert len(admin.get("/admin/doctors").json()) == 2


# --- Yönetici yetkisinin sınırları ----------------------------------------------


def test_admin_endpoints_are_admin_only(anon, make_user):
    parent = make_user("parent")
    doctor = make_user("doctor")
    for path in ("/admin/overview", "/admin/doctors", "/admin/audit"):
        assert anon.get(path).status_code == 401, path
        assert parent.get(path).status_code == 403, path
        assert doctor.get(path).status_code == 403, path
    assert doctor.post(f"/admin/doctors/{doctor.user['id']}/approve", json={}).status_code == 403


def test_admin_cannot_read_health_data(admin, parent_with_toddler):
    parent, child = parent_with_toddler
    assert admin.get("/subjects").json() == []
    for path in ("", "/logs", "/screenings", "/notes", "/insights", "/access-log"):
        assert admin.get(f"/subjects/{child['id']}{path}").status_code == 404, path
    assert admin.get("/conversations").json() == []
    assert admin.post(f"/conversations/{parent.user['id']}/messages", json={"body": "x"}).status_code == 404


# --- Erişim günlüğü ---------------------------------------------------------------


def test_owner_sees_who_accessed_their_record(app, make_user, parent_with_toddler):
    parent, child = parent_with_toddler
    doctor = make_user("doctor", email="dr.iz@example.com")
    _care_team_add(parent, child["id"], "dr.iz@example.com")
    base = f"/subjects/{child['id']}"
    doctor.get(base)
    doctor.get(f"{base}/logs")
    doctor.post(f"{base}/notes", json={"body": "Kontrol"})
    parent.get(f"{base}/logs")  # sahibin kendi işlemleri listede yer almaz

    history = parent.get(f"{base}/access-log").json()
    assert [e["action"] for e in history] == ["note.create", "log.list", "subject.view"]
    assert {e["actor_label"] for e in history} == {"Test Doctor"}
    assert "ip" not in history[0] and "actor_id" not in history[0]

    assert doctor.get(f"{base}/access-log").status_code == 403  # yalnızca veri sahibi
    assert make_user("parent").get(f"{base}/access-log").status_code == 404


def test_denied_attempts_are_recorded(app, make_user, parent_with_toddler):
    _, child = parent_with_toddler
    stranger = make_user("parent", email="meraklı@example.com")
    stranger.get(f"/subjects/{child['id']}/notes")

    [event] = audit_events(app, action="note.list", subject_id=child["id"])
    assert (event.outcome, event.status_code, event.actor_id) == ("denied", 404, stranger.user["id"])


def test_logins_are_recorded_with_attempted_email(app, anon, make_user):
    user = make_user("adult", email="giris@example.com")
    anon.post("/auth/login", json={"email": "giris@example.com", "password": "yanlis-sifre"})
    anon.post("/auth/login", json={"email": "giris@example.com", "password": "correct-horse-1"})

    failed, ok = audit_events(app, action="auth.login")
    assert (failed.outcome, failed.actor_id, failed.actor_label) == ("denied", None, "giris@example.com")
    assert (ok.outcome, ok.actor_id) == ("ok", user.user["id"])


def test_assistant_context_and_admin_actions_are_attributed(app, admin, make_user, parent_with_toddler):
    parent, child = parent_with_toddler
    parent.post("/assistant/chat", json={"message": "Uyku nasıl?", "subject_id": child["id"]})
    [chat] = audit_events(app, action="assistant.chat")
    assert chat.subject_id == child["id"]

    doctor = make_user("doctor", approved=False)
    admin.post(f"/admin/doctors/{doctor.user['id']}/approve", json={})
    [approval] = audit_events(app, action="admin.doctor.approve")
    assert (approval.actor_id, approval.target_user_id) == (admin.user["id"], doctor.user["id"])


def test_routine_requests_are_not_logged(app, parent_with_toddler):
    parent, _ = parent_with_toddler
    parent.get("/notifications")
    parent.get("/auth/me")
    assert audit_events(app, action="notifications") == []
    assert {e.action for e in audit_events(app)} <= {"auth.register", "subject.create"}


def test_admin_audit_filters_and_pagination(admin, make_user, parent_with_toddler):
    _, child = parent_with_toddler
    stranger = make_user("parent")
    for _ in range(3):
        stranger.get(f"/subjects/{child['id']}")

    denied = admin.get("/admin/audit", params={"outcome": "denied", "subject_id": child["id"]}).json()
    assert len(denied["items"]) == 3 and denied["next_before_id"] is None

    first = admin.get("/admin/audit", params={"limit": 2}).json()
    assert len(first["items"]) == 2 and first["next_before_id"] == first["items"][-1]["id"]
    second = admin.get("/admin/audit", params={"limit": 2, "before_id": first["next_before_id"]}).json()
    assert second["items"][0]["id"] < first["items"][-1]["id"]

    by_prefix = admin.get("/admin/audit", params={"action": "auth."}).json()["items"]
    assert by_prefix and all(e["action"].startswith("auth.") for e in by_prefix)

    overview = admin.get("/admin/overview").json()
    assert overview["denied_last_24h"] >= 3
    assert overview["users_by_role"]["admin"] == 1
