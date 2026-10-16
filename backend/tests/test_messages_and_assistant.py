from app.services import assistant


def test_messaging_requires_care_team_relationship(make_user, parent_with_toddler):
    parent, child = parent_with_toddler
    doctor = make_user("doctor", email="dr.mesaj@example.com")

    assert parent.post(f"/conversations/{doctor.user['id']}/messages", json={"body": "Merhaba"}).status_code == 404
    assert parent.get("/conversations").json() == []

    parent.post(f"/subjects/{child['id']}/care-team", json={"email": "dr.mesaj@example.com"})
    sent = parent.post(f"/conversations/{doctor.user['id']}/messages", json={"body": "Merhaba hocam"})
    assert sent.status_code == 201

    inbox = doctor.get("/conversations").json()
    assert inbox[0]["user"]["id"] == parent.user["id"]
    assert inbox[0]["unread"] == 1

    thread = doctor.get(f"/conversations/{parent.user['id']}/messages").json()
    assert [m["body"] for m in thread] == ["Merhaba hocam"]
    assert doctor.get("/conversations").json()[0]["unread"] == 0


def test_users_with_same_role_cannot_message(make_user):
    a, b = make_user("parent"), make_user("parent")
    assert a.post(f"/conversations/{b.user['id']}/messages", json={"body": "selam"}).status_code == 404


def test_blank_message_is_rejected(make_user, parent_with_toddler):
    parent, child = parent_with_toddler
    doctor = make_user("doctor", email="dr.bos@example.com")
    parent.post(f"/subjects/{child['id']}/care-team", json={"email": "dr.bos@example.com"})
    assert parent.post(f"/conversations/{doctor.user['id']}/messages", json={"body": "   "}).status_code == 422


def test_assistant_falls_back_without_api_key_and_flags_crisis(make_user, monkeypatch):
    monkeypatch.setattr(assistant.get_settings(), "gemini_api_key", None)
    adult = make_user("adult")

    normal = adult.post("/assistant/chat", json={"message": "Bu hafta uyku düzenim çok bozuldu"}).json()
    assert normal["source"] == "fallback"
    assert "Uyku" in normal["reply"]

    crisis = adult.post("/assistant/chat", json={"message": "Artık yaşamak istemiyorum"}).json()
    assert crisis["reply"].startswith(assistant.CRISIS_NOTE)


def test_assistant_cannot_read_context_of_foreign_subject(make_user, parent_with_toddler):
    _, child = parent_with_toddler
    stranger = make_user("adult")
    response = stranger.post("/assistant/chat", json={"message": "özet", "subject_id": child["id"]})
    assert response.status_code == 404
