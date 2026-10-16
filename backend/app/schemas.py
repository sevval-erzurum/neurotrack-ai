from datetime import UTC, date, datetime
from typing import Annotated, Any, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field, StringConstraints

from app.models import Role, SubjectKind


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


class RegisterIn(BaseModel):
    full_name: Name
    email: EmailStr
    password: Annotated[str, Field(min_length=8, max_length=72)]
    role: Role
    birth_date: date | None = None


class LoginIn(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(max_length=72)]


class UserOut(ORM):
    id: int
    email: str
    full_name: str
    role: Role


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
