"""Yönetici uçları: doktor başvurularının incelenmesi ve erişim günlüğü.

Yönetici sağlık verisine erişemez: subject uçları onun için 404 döner (bkz. access.py).
Burada yalnızca hesap bilgisi ve günlük kayıtları vardır.
"""

from datetime import timedelta

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select

from app.core.deps import DB, CurrentUser, require_role
from app.models import AuditEvent, CareTeamMember, DoctorStatus, Role, User, utcnow
from app.schemas import AdminOverview, AuditPage, DoctorApplicationOut, ReasonIn, ReviewIn
from app.services.notify import notify

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[require_role(Role.ADMIN)])

# Durum geçişleri: (hedef durum) -> izin verilen mevcut durumlar
_TRANSITIONS = {
    DoctorStatus.APPROVED: {DoctorStatus.PENDING, DoctorStatus.REJECTED, DoctorStatus.SUSPENDED},
    DoctorStatus.REJECTED: {DoctorStatus.PENDING},
    DoctorStatus.SUSPENDED: {DoctorStatus.APPROVED},
}

_MESSAGES = {
    DoctorStatus.APPROVED: ("Hesabınız onaylandı", "Artık danışanlar sizi bakım ekiplerine ekleyebilir."),
    DoctorStatus.REJECTED: ("Başvurunuz reddedildi", "Gerekçe: {reason}"),
    DoctorStatus.SUSPENDED: ("Hesabınız askıya alındı", "Danışan verilerine erişiminiz durduruldu. Gerekçe: {reason}"),
}


@router.get("/overview", response_model=AdminOverview)
def overview(db: DB) -> AdminOverview:
    since = utcnow() - timedelta(hours=24)
    users_by_role = dict(db.execute(select(User.role, func.count()).group_by(User.role)).all())
    doctors_by_status = dict(
        db.execute(select(User.doctor_status, func.count()).where(User.role == Role.DOCTOR).group_by(User.doctor_status)).all()
    )

    def count(*where) -> int:
        return db.scalar(select(func.count()).select_from(AuditEvent).where(AuditEvent.created_at >= since, *where)) or 0

    return AdminOverview(
        users_by_role={str(k): v for k, v in users_by_role.items()},
        doctors_by_status={str(k): v for k, v in doctors_by_status.items() if k},
        denied_last_24h=count(AuditEvent.outcome == "denied", AuditEvent.action != "auth.login"),
        failed_logins_last_24h=count(AuditEvent.action == "auth.login", AuditEvent.outcome == "denied"),
        events_last_24h=count(),
    )


@router.get("/doctors", response_model=list[DoctorApplicationOut])
def list_doctors(db: DB, status_filter: DoctorStatus | None = Query(None, alias="status")) -> list[DoctorApplicationOut]:
    patients = select(CareTeamMember.doctor_id, func.count().label("n")).group_by(CareTeamMember.doctor_id).subquery()
    stmt = (
        select(User, func.coalesce(patients.c.n, 0))
        .outerjoin(patients, patients.c.doctor_id == User.id)
        .where(User.role == Role.DOCTOR)
        .order_by(User.created_at.desc())
    )
    if status_filter is not None:
        stmt = stmt.where(User.doctor_status == status_filter)
    return [
        DoctorApplicationOut.model_validate(doctor).model_copy(update={"patient_count": n})
        for doctor, n in db.execute(stmt).all()
    ]


def _review(db: DB, admin: User, user_id: int, target: DoctorStatus, reason: str | None) -> DoctorApplicationOut:
    doctor = db.get(User, user_id)
    if doctor is None or doctor.role != Role.DOCTOR:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Doktor bulunamadı.")
    if doctor.doctor_status not in _TRANSITIONS[target]:
        raise HTTPException(status.HTTP_409_CONFLICT, "Hesabın mevcut durumunda bu işlem yapılamaz.")

    doctor.doctor_status = target
    doctor.status_reason = reason
    doctor.reviewed_at = utcnow()
    doctor.reviewed_by_id = admin.id
    title, body = _MESSAGES[target]
    notify(db, doctor.id, "account", title, body.format(reason=reason or "-"), "/dashboard")
    db.commit()
    return DoctorApplicationOut.model_validate(doctor)


@router.post("/doctors/{user_id}/approve", response_model=DoctorApplicationOut)
def approve(user_id: int, data: ReviewIn, admin: CurrentUser, db: DB) -> DoctorApplicationOut:
    return _review(db, admin, user_id, DoctorStatus.APPROVED, data.reason)


@router.post("/doctors/{user_id}/reject", response_model=DoctorApplicationOut)
def reject(user_id: int, data: ReasonIn, admin: CurrentUser, db: DB) -> DoctorApplicationOut:
    return _review(db, admin, user_id, DoctorStatus.REJECTED, data.reason)


@router.post("/doctors/{user_id}/suspend", response_model=DoctorApplicationOut)
def suspend(user_id: int, data: ReasonIn, admin: CurrentUser, db: DB) -> DoctorApplicationOut:
    return _review(db, admin, user_id, DoctorStatus.SUSPENDED, data.reason)


@router.get("/audit", response_model=AuditPage)
def audit_events(
    db: DB,
    actor_id: int | None = None,
    subject_id: int | None = None,
    outcome: str | None = Query(None, pattern="^(ok|denied|error)$"),
    action: str | None = Query(None, max_length=48, description="Önek eşleşmesi, ör. 'auth.' veya 'note.'"),
    before_id: int | None = None,
    limit: int = Query(50, ge=1, le=200),
) -> AuditPage:
    stmt = select(AuditEvent).order_by(AuditEvent.id.desc()).limit(limit + 1)
    if actor_id is not None:
        stmt = stmt.where(AuditEvent.actor_id == actor_id)
    if subject_id is not None:
        stmt = stmt.where(AuditEvent.subject_id == subject_id)
    if outcome is not None:
        stmt = stmt.where(AuditEvent.outcome == outcome)
    if action:
        stmt = stmt.where(AuditEvent.action.startswith(action, autoescape=True))
    if before_id is not None:
        stmt = stmt.where(AuditEvent.id < before_id)
    rows = list(db.scalars(stmt))
    more = len(rows) > limit
    rows = rows[:limit]
    return AuditPage(items=rows, next_before_id=rows[-1].id if more else None)
