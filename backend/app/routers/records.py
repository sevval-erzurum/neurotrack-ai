from datetime import date, timedelta

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.deps import DB, CurrentUser
from app.models import ClinicalObservation, DailyLog, DoctorNote, Role
from app.schemas import DailyLogIn, DailyLogOut, NoteIn, NoteOut, ObservationIn, ObservationOut
from app.services.access import Access, get_subject
from app.services.notify import notify

router = APIRouter(prefix="/subjects/{subject_id}", tags=["records"])


# --- Günlük kayıt (gün başına bir kayıt; aynı gün tekrar gönderilirse güncellenir) ---


@router.get("/logs", response_model=list[DailyLogOut])
def list_logs(subject_id: int, user: CurrentUser, db: DB, days: int = 90) -> list[DailyLog]:
    get_subject(db, user, subject_id)
    since = date.today() - timedelta(days=max(1, min(days, 730)))
    return list(
        db.scalars(
            select(DailyLog)
            .where(DailyLog.subject_id == subject_id, DailyLog.log_date > since)
            .order_by(DailyLog.log_date.desc())
        )
    )


@router.put("/logs", response_model=DailyLogOut)
def upsert_log(subject_id: int, data: DailyLogIn, user: CurrentUser, db: DB) -> DailyLog:
    get_subject(db, user, subject_id, Access.OWNER)
    if data.log_date > date.today():
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Gelecek tarihli kayıt eklenemez.")

    log = db.scalar(select(DailyLog).where(DailyLog.subject_id == subject_id, DailyLog.log_date == data.log_date))
    if log is None:
        log = DailyLog(subject_id=subject_id)
        db.add(log)
    for field, value in data.model_dump().items():
        setattr(log, field, value)
    log.author_id = user.id
    db.commit()
    return log


@router.delete("/logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_log(subject_id: int, log_id: int, user: CurrentUser, db: DB) -> None:
    get_subject(db, user, subject_id, Access.OWNER)
    log = db.get(DailyLog, log_id)
    if log is None or log.subject_id != subject_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Kayıt bulunamadı.")
    db.delete(log)
    db.commit()


# --- Klinik gözlem ---------------------------------------------------------


@router.get("/observations", response_model=list[ObservationOut])
def list_observations(subject_id: int, user: CurrentUser, db: DB) -> list[ClinicalObservation]:
    get_subject(db, user, subject_id)
    return list(
        db.scalars(
            select(ClinicalObservation)
            .where(ClinicalObservation.subject_id == subject_id)
            .order_by(ClinicalObservation.created_at.desc())
        )
    )


@router.post("/observations", response_model=ObservationOut, status_code=status.HTTP_201_CREATED)
def create_observation(subject_id: int, data: ObservationIn, user: CurrentUser, db: DB) -> ClinicalObservation:
    subject = get_subject(db, user, subject_id, Access.OBSERVE)
    observation = ClinicalObservation(subject_id=subject_id, author_id=user.id, **data.model_dump())
    db.add(observation)

    link = f"/subjects/{subject_id}"
    if data.self_harm_risk == "high":
        for member in subject.care_team:
            notify(
                db,
                member.doctor_id,
                "risk",
                "Acil: yüksek risk bildirimi",
                f"{subject.name} için yüksek kendine zarar riski bildirildi.",
                link,
            )
    if user.role == Role.DOCTOR:
        notify(
            db,
            subject.owner_id,
            "observation",
            "Yeni klinik gözlem",
            f"{user.full_name}, {subject.name} için klinik gözlem ekledi.",
            link,
        )
    db.commit()
    return observation


# --- Doktor notu -----------------------------------------------------------


@router.get("/notes", response_model=list[NoteOut])
def list_notes(subject_id: int, user: CurrentUser, db: DB) -> list[DoctorNote]:
    get_subject(db, user, subject_id)
    return list(db.scalars(select(DoctorNote).where(DoctorNote.subject_id == subject_id).order_by(DoctorNote.created_at.desc())))


@router.post("/notes", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(subject_id: int, data: NoteIn, user: CurrentUser, db: DB) -> DoctorNote:
    subject = get_subject(db, user, subject_id, Access.CLINICIAN)
    note = DoctorNote(subject_id=subject_id, doctor=user, **data.model_dump())
    db.add(note)

    visit = f" Sonraki görüşme: {data.next_visit:%d.%m.%Y}." if data.next_visit else ""
    notify(
        db,
        subject.owner_id,
        "note",
        "Yeni doktor notu",
        f"{user.full_name}, {subject.name} için not ekledi.{visit}",
        f"/subjects/{subject_id}",
    )
    db.commit()
    return note
