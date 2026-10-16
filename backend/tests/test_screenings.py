import math

from app.ml import aq10, toddler
from tests.conftest import months_ago


def qchat_answers(client, value: int) -> dict[str, int]:
    items = client.get("/screenings/instruments").json()["qchat10"]["items"]
    return {str(item["item"]): value for item in items}


def test_instruments_expose_model_operating_point(anon):
    data = anon.get("/screenings/instruments").json()
    assert len(data["qchat10"]["items"]) == 10
    assert all(len(item["options"]) == 5 for item in data["qchat10"]["items"])
    assert data["qchat10"]["model"]["sensitivity"] >= 0.9
    assert len(data["aq10"]["items"]) == 10


def test_qchat_returns_explained_risk(parent_with_toddler):
    parent, child = parent_with_toddler
    response = parent.post(
        f"/subjects/{child['id']}/screenings", json={"instrument": "qchat10", "answers": qchat_answers(parent, 4)}
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["risk_level"] == "high"
    contributions = body["details"]["contributions"]
    assert len(contributions) == 10
    # Katkılar büyüklüğe göre sıralı; en güçlü katkı riski artıran yönde olmalı.
    assert contributions[0]["log_odds"] > 0
    assert sum(c["log_odds"] for c in contributions) > 0

    typical = parent.post(
        f"/subjects/{child['id']}/screenings", json={"instrument": "qchat10", "answers": qchat_answers(parent, 0)}
    ).json()
    assert typical["risk_level"] == "low"
    assert typical["score"] < body["score"]


def test_qchat_rejects_children_outside_validated_age(make_user):
    parent = make_user("parent")
    older = parent.post("/subjects", json={"name": "Büyük Çocuk", "birth_date": months_ago(40).isoformat()}).json()
    response = parent.post(
        f"/subjects/{older['id']}/screenings", json={"instrument": "qchat10", "answers": qchat_answers(parent, 2)}
    )
    assert response.status_code == 422
    assert "18–24" in response.json()["detail"]


def test_qchat_requires_all_items(parent_with_toddler):
    parent, child = parent_with_toddler
    answers = qchat_answers(parent, 1)
    answers.pop(next(iter(answers)))
    response = parent.post(f"/subjects/{child['id']}/screenings", json={"instrument": "qchat10", "answers": answers})
    assert response.status_code == 422


def test_aq10_only_for_adult_self_profile(make_user, parent_with_toddler):
    parent, child = parent_with_toddler
    answers = {str(i): 0 for i in range(1, 11)}
    assert parent.post(f"/subjects/{child['id']}/screenings", json={"instrument": "aq10", "answers": answers}).status_code == 422

    adult = make_user("adult")
    subject_id = adult.get("/subjects").json()[0]["id"]
    response = adult.post(f"/subjects/{subject_id}/screenings", json={"instrument": "aq10", "answers": answers})
    assert response.status_code == 201
    # Hepsine "kesinlikle katılıyorum": yalnızca katılımın puan aldığı 4 madde (1, 7, 8, 10) puanlanır.
    assert response.json()["score"] == 4
    assert response.json()["risk_level"] == "low"


def test_elevated_screening_notifies_care_team(make_user, parent_with_toddler):
    parent, child = parent_with_toddler
    doctor = make_user("doctor", email="dr.tarama@example.com")
    parent.post(f"/subjects/{child['id']}/care-team", json={"email": "dr.tarama@example.com"})
    parent.post(f"/subjects/{child['id']}/screenings", json={"instrument": "qchat10", "answers": qchat_answers(parent, 4)})

    kinds = [n["kind"] for n in doctor.get("/notifications").json()]
    assert "screening" in kinds


def test_aq10_scoring_key():
    # 2-6 ve 9 numaralı maddelerde "katılmıyorum" puan alır.
    answers = {i: 3 if i in (2, 3, 4, 5, 6, 9) else 0 for i in range(1, 11)}
    result = aq10.score(answers)
    assert result.score == 10
    assert result.refer


def test_linear_contributions_reconstruct_model_output():
    model, meta = toddler.load()
    answers = {entry["item"]: (entry["item"] * 7) % 5 for entry in meta["items"]}
    result = toddler.screen(answers)
    logit = math.log(result.probability / (1 - result.probability))
    reconstructed = sum(c.log_odds for c in result.contributions) + model.named_steps["clf"].intercept_[0]
    assert abs(logit - reconstructed) < 1e-2
