from datetime import UTC, date, datetime
from typing import Annotated, Any, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field, StringConstraints, model_validator

from app.models import DoctorStatus, Role, SubjectKind


def _as_utc(value: datetime) -> datetime:
    # SQLite saat dilimi bilgisini saklamaz; tüm zamanlar UTC olarak yazılır.
    return value if value.tzinfo else value.replace(tzinfo=UTC)


UTCDateTime = Annotated[datetime, AfterValidator(_as_utc)]
Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=120)]
Scale10 = Annotated[int, Field(ge=0, le=10)]
Mood = Literal["happy", "calm", "tired", "anxious", "sad", "angry"]
Sex = Literal["female", "male", "other"]


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# --- Kimlik ---------------------------------------------------------------


LicenseNumber = Annotated[str, StringConstraints(strip_whitespace=True, pattern=r"^[A-Za-z0-9/-]{4,32}$")]
Reason = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=500)]


class RegisterIn(BaseModel):
    full_name: Name
    email: EmailStr
    password: Annotated[str, Field(min_length=8, max_length=72)]
    # Yönetici hesabı kayıt formundan açılamaz; yalnızca `python -m app.cli create-admin` ile.
    role: Literal[Role.PARENT, Role.ADULT, Role.DOCTOR]
    birth_date: date | None = None
    # Doktor başvurusu: yönetici bu bilgilerle kimliği doğrular.
    license_number: LicenseNumber | None = None
    institution: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=200)] | None = None

    @model_validator(mode="after")
    def doctor_needs_credentials(self) -> "RegisterIn":
        if self.role == Role.DOCTOR and not (self.license_number and self.institution):
            raise ValueError("Doktor kaydı için diploma tescil numarası ve kurum gereklidir.")
        if self.role != Role.DOCTOR:
            self.license_number = self.institution = None
        return self


class LoginIn(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(max_length=72)]


class UserOut(ORM):
    id: int
    email: str
    full_name: str
    role: Role
    doctor_status: DoctorStatus | None = None
    status_reason: str | None = None


class UserBrief(ORM):
    id: int
    full_name: str
    role: Role


# --- Takip edilen kişi ----------------------------------------------------


class SubjectCreate(BaseModel):
    name: Name
    birth_date: date
    sex: Sex | None = None


class SubjectUpdate(BaseModel):
    name: Name | None = None
    birth_date: date | None = None
    sex: Sex | None = None


class DoctorOut(ORM):
    id: int
    full_name: str
    email: str
    institution: str | None = None
    doctor_status: DoctorStatus | None = None


class SubjectOut(ORM):
    id: int
    kind: SubjectKind
    name: str
    birth_date: date | None
    sex: str | None
    age_months: int | None
    owner: UserBrief
    care_team: list[DoctorOut]
    created_at: UTCDateTime


class CareTeamAdd(BaseModel):
    email: EmailStr


# --- Kayıtlar -------------------------------------------------------------


class DailyLogIn(BaseModel):
    log_date: date = Field(default_factory=date.today)
    mood: Mood
    sleep_hours: Annotated[float, Field(ge=0, le=24)]
    social_interaction: Scale10
    meltdown: bool = False
    note: Annotated[str, Field(max_length=2000)] | None = None


class DailyLogOut(ORM):
    id: int
    log_date: date
    mood: Mood
    sleep_hours: float
    social_interaction: int
    meltdown: bool
    note: str | None
    created_at: UTCDateTime


class ObservationIn(BaseModel):
    sensory_sensitivity: Scale10
    eye_contact: Scale10
    communication: Scale10
    routine_adaptation: Scale10
    eating_pattern: Annotated[str, Field(max_length=200)] | None = None
    therapy: Annotated[str, Field(max_length=200)] | None = None
    self_harm_risk: Literal["none", "low", "high"] = "none"
    note: Annotated[str, Field(max_length=2000)] | None = None


class ObservationOut(ObservationIn, ORM):
    id: int
    author_id: int | None
    created_at: UTCDateTime


class ScreeningIn(BaseModel):
    instrument: Literal["qchat10", "aq10"]
    answers: dict[int, Annotated[int, Field(ge=0, le=4)]]


class ScreeningOut(ORM):
    id: int
    instrument: str
    answers: dict[str, int]
    score: float
    risk_level: Literal["low", "elevated", "high"]
    details: dict[str, Any]
    created_at: UTCDateTime


class NoteIn(BaseModel):
    body: Annotated[str, Field(min_length=1, max_length=5000)]
    recommendation: Annotated[str, Field(max_length=2000)] | None = None
    next_visit: date | None = None


class NoteOut(ORM):
    id: int
    doctor: UserBrief | None
    body: str
    recommendation: str | None
    next_visit: date | None
    created_at: UTCDateTime


# --- İletişim -------------------------------------------------------------


class MessageIn(BaseModel):
    body: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)]


class MessageOut(ORM):
    id: int
    sender_id: int
    recipient_id: int
    body: str
    read_at: UTCDateTime | None
    created_at: UTCDateTime


class ConversationOut(BaseModel):
    user: UserBrief
    last_message: MessageOut | None
    unread: int


class NotificationOut(ORM):
    id: int
    kind: str
    title: str
    body: str
    link: str | None
    read_at: UTCDateTime | None
    created_at: UTCDateTime


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: Annotated[str, Field(max_length=4000)]


class ChatIn(BaseModel):
    message: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]
    subject_id: int | None = None
    history: Annotated[list[ChatTurn], Field(max_length=20)] = []


class ChatOut(BaseModel):
    reply: str
    source: Literal["gemini", "fallback"]


# --- Yönetim ----------------------------------------------------------------


class DoctorApplicationOut(ORM):
    id: int
    full_name: str
    email: str
    license_number: str | None
    institution: str | None
    doctor_status: DoctorStatus | None
    status_reason: str | None
    created_at: UTCDateTime
    reviewed_at: UTCDateTime | None
    patient_count: int = 0


class ReviewIn(BaseModel):
    reason: Reason | None = None


class ReasonIn(BaseModel):
    reason: Reason


class AuditEventOut(ORM):
    id: int
    created_at: UTCDateTime
    actor_id: int | None
    actor_role: str | None
    actor_label: str | None
    action: str
    outcome: Literal["ok", "denied", "error"]
    status_code: int
    subject_id: int | None
    target_user_id: int | None
    ip: str | None


class AuditPage(BaseModel):
    items: list[AuditEventOut]
    next_before_id: int | None


class AdminOverview(BaseModel):
    users_by_role: dict[str, int]
    doctors_by_status: dict[str, int]
    denied_last_24h: int
    failed_logins_last_24h: int
    events_last_24h: int


class AccessLogEntry(ORM):
    """Veri sahibine gösterilen geçmiş satırı: IP ve iç kimlikler yer almaz."""

    id: int
    created_at: UTCDateTime
    actor_label: str | None
    actor_role: str | None
    action: str
