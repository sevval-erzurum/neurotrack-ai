from datetime import date

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.deps import DB, CurrentUser, require_role
from app.models import CareTeamMember, DoctorStatus, Role, Subject, SubjectKind, User
from app.schemas import AccessLogEntry, CareTeamAdd, DoctorOut, SubjectCreate, SubjectOut, SubjectUpdate, UserBrief
from app.services import audit, insights
from app.services.access import Access, accessible_subjects, get_subject
from app.services.notify import notify

router = APIRouter(prefix="/subjects", tags=["subjects"])


class SubjectWithSummary(SubjectOut):
    summary: insights.Summary


def to_out(subject: Subject) -> SubjectOut:
    return SubjectOut(
        id=subject.id,
        kind=subject.kind,
        name=subject.name,
        birth_date=subject.birth_date,
        sex=subject.sex,
        age_months=subject.age_months(),
        owner=UserBrief.model_validate(subject.owner),
        care_team=[DoctorOut.model_validate(m.doctor) for m in subject.care_team],
        created_at=subject.created_at,
    )


@router.get("", response_model=list[SubjectWithSummary])
def list_subjects(user: CurrentUser, db: DB) -> list[SubjectWithSummary]:
    return [
        SubjectWithSummary(**to_out(s).model_dump(), summary=insights.summarize(db, s)) for s in accessible_subjects(db, user)
    ]


@router.post("", response_model=SubjectOut, status_code=status.HTTP_201_CREATED, dependencies=[require_role(Role.PARENT)])
def create_child(data: SubjectCreate, user: CurrentUser, db: DB) -> SubjectOut:
    if data.birth_date > date.today():
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Doğum tarihi gelecekte olamaz.")
    subject = Subject(owner=user, kind=SubjectKind.CHILD, **data.model_dump())
    db.add(subject)
    db.commit()
    return to_out(subject)


@router.get("/{subject_id}", response_model=SubjectOut)
def read_subject(subject_id: int, user: CurrentUser, db: DB) -> SubjectOut:
    return to_out(get_subject(db, user, subject_id))


@router.patch("/{subject_id}", response_model=SubjectOut)
def update_subject(subject_id: int, data: SubjectUpdate, user: CurrentUser, db: DB) -> SubjectOut:
    subject = get_subject(db, user, subject_id, Access.OWNER)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(subject, field, value)
    db.commit()
    return to_out(subject)


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(subject_id: int, user: CurrentUser, db: DB) -> None:
    subject = get_subject(db, user, subject_id, Access.OWNER)
    if subject.kind != SubjectKind.CHILD:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Kendi profiliniz silinemez.")
    db.delete(subject)
    db.commit()


@router.get("/{subject_id}/insights", response_model=insights.Insights)
def subject_insights(subject_id: int, user: CurrentUser, db: DB, days: int = 30) -> insights.Insights:
    subject = get_subject(db, user, subject_id)
    return insights.compute(db, subject, days=max(7, min(days, 365)))


# --- Bakım ekibi: erişimi verinin sahibi verir ---------------------------


@router.post("/{subject_id}/care-team", response_model=DoctorOut, status_code=status.HTTP_201_CREATED)
def add_doctor(subject_id: int, data: CareTeamAdd, user: CurrentUser, db: DB) -> User:
    subject = get_subject(db, user, subject_id, Access.OWNER)
    doctor = db.scalar(
        select(User).where(
            User.email == data.email.lower(), User.role == Role.DOCTOR, User.doctor_status == DoctorStatus.APPROVED
        )
    )
    if doctor is None:
        # Başvurusu bekleyen, reddedilen veya askıdaki doktorlar da aynı yanıtı alır.
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Bu e-postaya kayıtlı, onaylı bir doktor bulunamadı.")
    if any(m.doctor_id == doctor.id for m in subject.care_team):
        raise HTTPException(status.HTTP_409_CONFLICT, "Bu doktor zaten bakım ekibinde.")

    subject.care_team.append(CareTeamMember(doctor=doctor))
    notify(
        db,
        doctor.id,
        "care_team",
        "Yeni danışan",
        f"{user.full_name}, {subject.name} için sizi bakım ekibine ekledi.",
        f"/subjects/{subject.id}",
    )
    db.commit()
    return doctor


@router.delete("/{subject_id}/care-team/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_doctor(subject_id: int, doctor_id: int, user: CurrentUser, db: DB) -> None:
    subject = get_subject(db, user, subject_id)
    if user.id not in (subject.owner_id, doctor_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Bu işlem için yetkiniz yok.")
    member = next((m for m in subject.care_team if m.doctor_id == doctor_id), None)
    if member is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Doktor bakım ekibinde değil.")
    subject.care_team.remove(member)
    db.commit()


@router.get("/{subject_id}/access-log", response_model=list[AccessLogEntry])
def access_log(subject_id: int, user: CurrentUser, db: DB, limit: int = 100) -> list:
    """Veri sahibi, kaydına kendisi dışında kimin ne zaman eriştiğini görür."""
    subject = get_subject(db, user, subject_id, Access.OWNER)
    return audit.subject_history(db, subject, limit=min(limit, 500))
