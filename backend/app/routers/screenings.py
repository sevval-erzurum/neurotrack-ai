from dataclasses import asdict
from typing import Any

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.deps import DB, CurrentUser
from app.ml import aq10, toddler
from app.models import Screening, Subject, SubjectKind
from app.schemas import ScreeningIn, ScreeningOut
from app.services.access import Access, get_subject
from app.services.notify import notify

router = APIRouter(tags=["screenings"])

QCHAT_AGE_MONTHS = (18, 24)
AQ10_MIN_AGE_MONTHS = 16 * 12


@router.get("/screenings/instruments")
def instruments() -> dict[str, Any]:
    _, meta = toddler.load()
    op = meta["operating_point"]
    return {
        "qchat10": {
            "name": "Q-CHAT kısa form (küçük çocuk)",
            "description": "18–24 aylık çocuklar için ebeveyn tarafından doldurulan kısa form. "
            "Sonuç, gerçek tanılarla eğitilmiş bir makine öğrenmesi modelinden gelir.",
            "age_range_months": list(QCHAT_AGE_MONTHS),
            "items": meta["items"],
            "model": {
                "version": meta["model_version"],
                "label": meta["chosen_model_label"],
                "threshold": op["threshold"],
                "sensitivity": op["sensitivity"],
                "specificity": op["specificity"],
            },
        },
        "aq10": {
            "name": "AQ-10 (yetişkin)",
            "description": "16 yaş ve üzeri için 10 maddelik öz-bildirim ölçeği. "
            f"Puan {aq10.REFERRAL_THRESHOLD} ve üzerindeyse uzman değerlendirmesi önerilir.",
            "items": [{"item": i, "question": q, "options": aq10.OPTIONS} for i, (q, _) in aq10.ITEMS.items()],
            "threshold": aq10.REFERRAL_THRESHOLD,
        },
    }


def _run_qchat(subject: Subject, answers: dict[int, int]) -> tuple[float, str, dict]:
    age = subject.age_months()
    lo, hi = QCHAT_AGE_MONTHS
    if subject.kind != SubjectKind.CHILD or age is None or not lo <= age <= hi:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            f"Q-CHAT kısa formu yalnızca {lo}–{hi} aylık çocuklar için geçerlidir (model bu yaş aralığında eğitildi).",
        )
    result = toddler.screen(answers)
    details = {
        "threshold": result.threshold,
        "model_version": result.model_version,
        "contributions": [asdict(c) for c in result.contributions],
    }
    return result.probability, result.risk_level, details


def _run_aq10(subject: Subject, answers: dict[int, int]) -> tuple[float, str, dict]:
    age = subject.age_months()
    if subject.kind != SubjectKind.SELF or (age is not None and age < AQ10_MIN_AGE_MONTHS):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "AQ-10 yalnızca 16 yaş ve üzeri yetişkinler içindir.")
    result = aq10.score(answers)
    details = {"threshold": aq10.REFERRAL_THRESHOLD, "scored_items": result.scored_items}
    return float(result.score), "elevated" if result.refer else "low", details


RUNNERS = {"qchat10": _run_qchat, "aq10": _run_aq10}


@router.get("/subjects/{subject_id}/screenings", response_model=list[ScreeningOut])
def list_screenings(subject_id: int, user: CurrentUser, db: DB) -> list[Screening]:
    get_subject(db, user, subject_id)
    return list(db.scalars(select(Screening).where(Screening.subject_id == subject_id).order_by(Screening.created_at.desc())))


@router.post("/subjects/{subject_id}/screenings", response_model=ScreeningOut, status_code=status.HTTP_201_CREATED)
def create_screening(subject_id: int, data: ScreeningIn, user: CurrentUser, db: DB) -> Screening:
    subject = get_subject(db, user, subject_id, Access.OBSERVE)
    try:
        score, risk_level, details = RUNNERS[data.instrument](subject, data.answers)
    except ValueError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(error)) from error

    screening = Screening(
        subject_id=subject_id,
        author_id=user.id,
        instrument=data.instrument,
        answers={str(k): v for k, v in data.answers.items()},
        score=score,
        risk_level=risk_level,
        details=details,
    )
    db.add(screening)

    if risk_level != "low":
        for member in subject.care_team:
            notify(
                db,
                member.doctor_id,
                "screening",
                "Tarama sonucu: değerlendirme önerildi",
                f"{subject.name} için yapılan {data.instrument.upper()} taraması uzman değerlendirmesi öneriyor.",
                f"/subjects/{subject_id}",
            )
    db.commit()
    return screening


@router.get("/subjects/{subject_id}/screenings/{screening_id}", response_model=ScreeningOut)
def read_screening(subject_id: int, screening_id: int, user: CurrentUser, db: DB) -> Screening:
    get_subject(db, user, subject_id)
    screening = db.get(Screening, screening_id)
    if screening is None or screening.subject_id != subject_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tarama bulunamadı.")
    return screening
