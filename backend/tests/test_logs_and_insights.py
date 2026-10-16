from datetime import date, timedelta


def test_same_day_log_is_updated_not_duplicated(parent_with_toddler):
    parent, child = parent_with_toddler
    url = f"/subjects/{child['id']}/logs"
    parent.put(url, json={"mood": "sad", "sleep_hours": 7, "social_interaction": 3})
    parent.put(url, json={"mood": "happy", "sleep_hours": 9.5, "social_interaction": 8})

    logs = parent.get(url).json()
    assert len(logs) == 1
    assert logs[0]["mood"] == "happy"
    assert logs[0]["sleep_hours"] == 9.5


def test_future_log_and_invalid_values_are_rejected(parent_with_toddler):
    parent, child = parent_with_toddler
    url = f"/subjects/{child['id']}/logs"
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    future_log = {"log_date": tomorrow, "mood": "calm", "sleep_hours": 8, "social_interaction": 5}
    assert parent.put(url, json=future_log).status_code == 422
    assert parent.put(url, json={"mood": "calm", "sleep_hours": 30, "social_interaction": 5}).status_code == 422
    assert parent.put(url, json={"mood": "bored", "sleep_hours": 8, "social_interaction": 5}).status_code == 422


def test_insights_raise_alerts_and_count_streak(parent_with_toddler):
    parent, child = parent_with_toddler
    url = f"/subjects/{child['id']}/logs"
    today = date.today()
    for offset in range(4):
        day = (today - timedelta(days=offset)).isoformat()
        parent.put(
            url, json={"log_date": day, "mood": "anxious", "sleep_hours": 4.5, "social_interaction": 2, "meltdown": offset < 2}
        )

    insights = parent.get(f"/subjects/{child['id']}/insights").json()
    codes = {alert["code"] for alert in insights["alerts"]}
    assert {"low_sleep", "low_social", "negative_mood", "meltdowns"} <= codes
    assert insights["stats"]["streak"] == 4
    assert insights["stats"]["logged_today"] is True
    assert len(insights["series"]) == 4

    summary = parent.get("/subjects").json()[0]["summary"]
    assert summary["alert_count"] == 4


def test_high_self_harm_risk_is_critical_and_notifies_doctor(make_user, parent_with_toddler):
    parent, child = parent_with_toddler
    doctor = make_user("doctor", email="dr.acil@example.com")
    parent.post(f"/subjects/{child['id']}/care-team", json={"email": "dr.acil@example.com"})
    parent.post(
        f"/subjects/{child['id']}/observations",
        json={"sensory_sensitivity": 8, "eye_contact": 2, "communication": 3, "routine_adaptation": 3, "self_harm_risk": "high"},
    )

    alerts = parent.get(f"/subjects/{child['id']}/insights").json()["alerts"]
    assert alerts[0]["level"] == "critical"
    assert any(n["kind"] == "risk" for n in doctor.get("/notifications").json())


def test_doctor_note_with_upcoming_visit_appears_in_insights(make_user, parent_with_toddler):
    parent, child = parent_with_toddler
    doctor = make_user("doctor", email="dr.randevu@example.com")
    parent.post(f"/subjects/{child['id']}/care-team", json={"email": "dr.randevu@example.com"})
    visit = (date.today() + timedelta(days=2)).isoformat()
    doctor.post(f"/subjects/{child['id']}/notes", json={"body": "Konuşma terapisi önerildi.", "next_visit": visit})

    insights = parent.get(f"/subjects/{child['id']}/insights").json()
    assert insights["next_visit"] == visit
    notes = parent.get(f"/subjects/{child['id']}/notes").json()
    assert notes[0]["doctor"]["full_name"] == "Test Doctor"
