"""Eski API'de her endpoint user_id'yi istemciden alıyordu; bu testler o açığın kapandığını doğrular."""

from datetime import date


def test_parent_cannot_see_another_parents_child(make_user, parent_with_toddler):
    _, child = parent_with_toddler
    stranger = make_user("parent")

    for path in ("", "/logs", "/observations", "/screenings", "/notes", "/insights"):
        assert stranger.get(f"/subjects/{child['id']}{path}").status_code == 404, path
    assert stranger.get("/subjects").json() == []


def test_doctor_has_no_access_until_owner_adds_them(make_user, parent_with_toddler):
    parent, child = parent_with_toddler
    doctor = make_user("doctor", email="dr.kaya@example.com")
    assert doctor.get(f"/subjects/{child['id']}").status_code == 404

    added = parent.post(f"/subjects/{child['id']}/care-team", json={"email": "dr.kaya@example.com"})
    assert added.status_code == 201
    assert doctor.get(f"/subjects/{child['id']}").status_code == 200
    assert [s["id"] for s in doctor.get("/subjects").json()] == [child["id"]]


def test_doctor_cannot_add_themselves_to_a_care_team(make_user, parent_with_toddler):
    _, child = parent_with_toddler
    doctor = make_user("doctor", email="dr.self@example.com")
    response = doctor.post(f"/subjects/{child['id']}/care-team", json={"email": "dr.self@example.com"})
    assert response.status_code == 404


def test_only_doctors_can_be_added_to_care_team(make_user, parent_with_toddler):
    parent, child = parent_with_toddler
    make_user("adult", email="not.a.doctor@example.com")
    response = parent.post(f"/subjects/{child['id']}/care-team", json={"email": "not.a.doctor@example.com"})
    assert response.status_code == 404


def test_role_permissions_on_records(make_user, parent_with_toddler):
    parent, child = parent_with_toddler
    doctor = make_user("doctor", email="dr.rol@example.com")
    parent.post(f"/subjects/{child['id']}/care-team", json={"email": "dr.rol@example.com"})
    base = f"/subjects/{child['id']}"
    log = {"mood": "calm", "sleep_hours": 9, "social_interaction": 6}
    note = {"body": "Kontrol iyi geçti."}
    observation = {"sensory_sensitivity": 5, "eye_contact": 5, "communication": 5, "routine_adaptation": 5}

    assert doctor.put(f"{base}/logs", json=log).status_code == 403
    assert parent.post(f"{base}/notes", json=note).status_code == 403
    assert doctor.post(f"{base}/notes", json=note).status_code == 201
    assert doctor.post(f"{base}/observations", json=observation).status_code == 201
    assert doctor.delete(base).status_code == 403


def test_removing_doctor_revokes_access(make_user, parent_with_toddler):
    parent, child = parent_with_toddler
    doctor = make_user("doctor", email="dr.gecici@example.com")
    parent.post(f"/subjects/{child['id']}/care-team", json={"email": "dr.gecici@example.com"})

    assert parent.delete(f"/subjects/{child['id']}/care-team/{doctor.user['id']}").status_code == 204
    assert doctor.get(f"/subjects/{child['id']}").status_code == 404


def test_only_parents_can_add_children(make_user):
    for role in ("adult", "doctor"):
        client = make_user(role)
        assert client.post("/subjects", json={"name": "X Y", "birth_date": "2024-01-01"}).status_code == 403


def test_adult_cannot_delete_own_profile(make_user):
    adult = make_user("adult")
    subject_id = adult.get("/subjects").json()[0]["id"]
    assert adult.delete(f"/subjects/{subject_id}").status_code == 400


def test_deleting_child_removes_its_records(make_user, parent_with_toddler):
    parent, child = parent_with_toddler
    parent.put(f"/subjects/{child['id']}/logs", json={"mood": "happy", "sleep_hours": 10, "social_interaction": 7})
    assert parent.delete(f"/subjects/{child['id']}").status_code == 204
    assert parent.get(f"/subjects/{child['id']}/logs").status_code == 404


def test_notification_ids_of_other_users_are_not_accessible(make_user, parent_with_toddler):
    parent, child = parent_with_toddler
    doctor = make_user("doctor", email="dr.bildirim@example.com")
    parent.post(f"/subjects/{child['id']}/care-team", json={"email": "dr.bildirim@example.com"})
    doctor_notification = doctor.get("/notifications").json()[0]

    assert parent.post(f"/notifications/{doctor_notification['id']}/read").status_code == 404


def test_future_birth_date_is_rejected(make_user):
    parent = make_user("parent")
    future = date(date.today().year + 1, 1, 1).isoformat()
    assert parent.post("/subjects", json={"name": "Gelecek Bebek", "birth_date": future}).status_code == 422
