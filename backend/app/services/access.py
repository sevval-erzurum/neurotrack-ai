"""Subject erişim kuralları — yetkilendirmenin tek kaynağı.

Erişimi olmayan bir subject için 403 yerine 404 döner; böylece başka kullanıcılara
ait kayıtların varlığı ID tahminiyle öğrenilemez.

Doktor erişimi iki koşula bağlıdır: hesabın yönetici tarafından onaylı olması ve veri sahibinin
doktoru bakım ekibine eklemiş olması. Onay kaldırılırsa (askıya alma) erişim anında kesilir;
bakım ekibi kaydı silinmez, onay geri gelirse erişim de geri gelir.
"""

from enum import Enum

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CareTeamMember, DoctorStatus, Role, Subject, User


class Access(Enum):
    READ = "read"  # sahip veya bakım ekibindeki onaylı doktor
    OBSERVE = "observe"  # klinik gözlem ve tarama ekleme: sahip veya doktor
    OWNER = "owner"  # günlük kayıt, bakım ekibi yönetimi, silme
    CLINICIAN = "clinician"  # doktor notu: yalnızca bakım ekibindeki doktor


def is_on_care_team(db: Session, subject_id: int, doctor_id: int) -> bool:
    return (
        db.scalar(select(CareTeamMember.id).where(CareTeamMember.subject_id == subject_id, CareTeamMember.doctor_id == doctor_id))
        is not None
    )


def get_subject(db: Session, user: User, subject_id: int, access: Access = Access.READ) -> Subject:
    subject = db.get(Subject, subject_id)
    is_owner = subject is not None and subject.owner_id == user.id
    is_doctor = subject is not None and user.is_verified_doctor and is_on_care_team(db, subject.id, user.id)

    if not (is_owner or is_doctor):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Kayıt bulunamadı.")

    allowed = {
        Access.READ: True,
        Access.OBSERVE: True,
        Access.OWNER: is_owner,
        Access.CLINICIAN: is_doctor,
    }[access]
    if not allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Bu işlem için yetkiniz yok.")
    return subject


def accessible_subjects(db: Session, user: User) -> list[Subject]:
    if user.role == Role.ADMIN or (user.role == Role.DOCTOR and not user.is_verified_doctor):
        return []
    if user.role == Role.DOCTOR:
        stmt = (
            select(Subject)
            .join(CareTeamMember, CareTeamMember.subject_id == Subject.id)
            .where(CareTeamMember.doctor_id == user.id)
        )
    else:
        stmt = select(Subject).where(Subject.owner_id == user.id)
    return list(db.scalars(stmt.order_by(Subject.created_at)))


def can_message(db: Session, a: User, b: User) -> bool:
    """İki kullanıcı, biri diğerinin subject'inin bakım ekibindeyse mesajlaşabilir."""
    if a.role == b.role or Role.DOCTOR not in (a.role, b.role) or Role.ADMIN in (a.role, b.role):
        return False
    doctor, owner = (a, b) if a.role == Role.DOCTOR else (b, a)
    if doctor.doctor_status != DoctorStatus.APPROVED:
        return False
    return (
        db.scalar(
            select(CareTeamMember.id)
            .join(Subject, Subject.id == CareTeamMember.subject_id)
            .where(CareTeamMember.doctor_id == doctor.id, Subject.owner_id == owner.id)
            .limit(1)
        )
        is not None
    )
