"""Veri modeli.

Takip edilen her kişi bir `Subject`tir: yetişkin kullanıcının kendisi (kind="self") ya da
ebeveynin eklediği bir çocuk (kind="child"). Günlük kayıtlar, klinik gözlemler, taramalar
ve doktor notları yalnızca subject'e bağlanır; erişim kuralı tek yerde tanımlanır
(app/services/access.py): subject'in sahibi veya bakım ekibindeki onaylı doktor.

Yönetici hesapları yönetir (doktor onayı, erişim günlüğü) ama sağlık verisine erişemez.
"""

from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class Role(StrEnum):
    ADULT = "adult"
    PARENT = "parent"
    DOCTOR = "doctor"
    ADMIN = "admin"


class DoctorStatus(StrEnum):
    PENDING = "pending"  # kayıt oldu, yönetici incelemesi bekliyor
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"  # onaylıydı; erişimi yönetici tarafından durduruldu


class SubjectKind(StrEnum):
    SELF = "self"
    CHILD = "child"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(128))
    full_name: Mapped[str] = mapped_column(String(120))
    role: Mapped[Role] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # Yalnızca doktorlar için. Onaylanmamış doktor hiçbir bakım ekibine eklenemez ve veri göremez.
    doctor_status: Mapped[DoctorStatus | None] = mapped_column(String(16))
    license_number: Mapped[str | None] = mapped_column(String(32))
    institution: Mapped[str | None] = mapped_column(String(200))
    status_reason: Mapped[str | None] = mapped_column(Text)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reviewed_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    subjects: Mapped[list["Subject"]] = relationship(back_populates="owner", cascade="all, delete-orphan")

    @property
    def is_verified_doctor(self) -> bool:
        return self.role == Role.DOCTOR and self.doctor_status == DoctorStatus.APPROVED


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    kind: Mapped[SubjectKind] = mapped_column(String(8))
    name: Mapped[str] = mapped_column(String(120))
    birth_date: Mapped[date | None] = mapped_column(Date)
    sex: Mapped[str | None] = mapped_column(String(8))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    owner: Mapped[User] = relationship(back_populates="subjects")
    care_team: Mapped[list["CareTeamMember"]] = relationship(back_populates="subject", cascade="all, delete-orphan")
    daily_logs: Mapped[list["DailyLog"]] = relationship(cascade="all, delete-orphan")
    observations: Mapped[list["ClinicalObservation"]] = relationship(cascade="all, delete-orphan")
    screenings: Mapped[list["Screening"]] = relationship(cascade="all, delete-orphan")
    notes: Mapped[list["DoctorNote"]] = relationship(cascade="all, delete-orphan")

    def age_months(self, today: date | None = None) -> int | None:
        if self.birth_date is None:
            return None
        today = today or date.today()
        months = (today.year - self.birth_date.year) * 12 + today.month - self.birth_date.month
        return months - (today.day < self.birth_date.day)


class CareTeamMember(Base):
    __tablename__ = "care_team_members"
    __table_args__ = (UniqueConstraint("subject_id", "doctor_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    subject: Mapped[Subject] = relationship(back_populates="care_team")
    doctor: Mapped[User] = relationship()


class DailyLog(Base):
    __tablename__ = "daily_logs"
    __table_args__ = (UniqueConstraint("subject_id", "log_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True)
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    log_date: Mapped[date] = mapped_column(Date)
    mood: Mapped[str] = mapped_column(String(16))
    sleep_hours: Mapped[float]
    social_interaction: Mapped[int]
    meltdown: Mapped[bool] = mapped_column(default=False)
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ClinicalObservation(Base):
    __tablename__ = "clinical_observations"

    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True)
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    sensory_sensitivity: Mapped[int]
    eye_contact: Mapped[int]
    communication: Mapped[int]
    routine_adaptation: Mapped[int]
    eating_pattern: Mapped[str | None] = mapped_column(String(200))
    therapy: Mapped[str | None] = mapped_column(String(200))
    self_harm_risk: Mapped[str] = mapped_column(String(8), default="none")
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Screening(Base):
    __tablename__ = "screenings"

    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True)
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    instrument: Mapped[str] = mapped_column(String(16))
    answers: Mapped[dict[str, int]] = mapped_column(JSON)
    score: Mapped[float]
    risk_level: Mapped[str] = mapped_column(String(16))
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class DoctorNote(Base):
    __tablename__ = "doctor_notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True)
    doctor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    body: Mapped[str] = mapped_column(Text)
    recommendation: Mapped[str | None] = mapped_column(Text)
    next_visit: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    doctor: Mapped[User | None] = relationship()


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    recipient_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    body: Mapped[str] = mapped_column(Text)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(32))
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    link: Mapped[str | None] = mapped_column(String(200))
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AuditEvent(Base):
    """Erişim günlüğü: kim, ne zaman, hangi kayda, ne yaptı ve sonuç ne oldu.

    İstek gövdesi saklanmaz; günlükte sağlık verisi bulunmaz. subject_id ve kullanıcı alanları
    bilinçli olarak yabancı anahtar değildir: kayıt silinse de iz kalır.
    """

    __tablename__ = "audit_events"
    __table_args__ = (Index("ix_audit_subject_created", "subject_id", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    actor_id: Mapped[int | None] = mapped_column(index=True)
    actor_role: Mapped[str | None] = mapped_column(String(16))
    actor_label: Mapped[str | None] = mapped_column(String(320))  # ad veya (başarısız girişte) denenen e-posta
    action: Mapped[str] = mapped_column(String(48), index=True)
    outcome: Mapped[str] = mapped_column(String(8), index=True)  # ok | denied | error
    status_code: Mapped[int]
    subject_id: Mapped[int | None]
    target_user_id: Mapped[int | None]
    ip: Mapped[str | None] = mapped_column(String(64))
