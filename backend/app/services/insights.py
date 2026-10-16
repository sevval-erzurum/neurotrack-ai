"""Günlük kayıtlardan istatistik ve kural tabanlı takip uyarıları.

Uyarılar klinik karar değildir; ebeveyn/kullanıcı ve doktora "buna bakın" sinyali verir.
Eşikler bilinçli olarak basit ve açıklanabilir tutulmuştur.
"""

from collections import Counter
from datetime import date, timedelta
from typing import Literal

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ClinicalObservation, DailyLog, DoctorNote, Screening, Subject

NEGATIVE_MOODS = {"anxious", "sad", "angry"}
RECENT_DAYS = 7
MIN_LOGS_FOR_ALERTS = 3
LOW_SLEEP_HOURS = 6.0
LOW_SOCIAL = 4.0


class Alert(BaseModel):
    level: Literal["info", "warning", "critical"]
    code: str
    message: str


class Stats(BaseModel):
    n_logs: int
    avg_sleep: float | None
    avg_social: float | None
    meltdown_days: int
    mood_counts: dict[str, int]
    streak: int
    logged_today: bool


class Point(BaseModel):
    date: date
    sleep_hours: float
    social_interaction: int
    mood: str
    meltdown: bool


class LatestScreening(BaseModel):
    id: int
    instrument: str
    risk_level: str
    score: float
    created_at: str


class Insights(BaseModel):
    stats: Stats
    series: list[Point]
    alerts: list[Alert]
    latest_screening: LatestScreening | None
    next_visit: date | None


class Summary(BaseModel):
    latest_risk: str | None
    last_log_date: date | None
    alert_count: int
    next_visit: date | None


def _streak(dates: set[date], today: date) -> int:
    day = today if today in dates else today - timedelta(days=1)
    count = 0
    while day in dates:
        count += 1
        day -= timedelta(days=1)
    return count


def _avg(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 1) if values else None


def _alerts(
    recent: list[DailyLog],
    observation: ClinicalObservation | None,
    screening: Screening | None,
    next_visit: date | None,
    today: date,
) -> list[Alert]:
    alerts: list[Alert] = []

    if observation and observation.self_harm_risk == "high":
        alerts.append(
            Alert(
                level="critical",
                code="self_harm",
                message="Son klinik gözlemde yüksek kendine zarar riski bildirildi. Uzmanla hemen iletişime geçin.",
            )
        )

    if len(recent) >= MIN_LOGS_FOR_ALERTS:
        n = len(recent)
        sleep = sum(log.sleep_hours for log in recent) / n
        social = sum(log.social_interaction for log in recent) / n
        negative = sum(log.mood in NEGATIVE_MOODS for log in recent)
        meltdowns = sum(log.meltdown for log in recent)
        if sleep < LOW_SLEEP_HOURS:
            alerts.append(Alert(level="warning", code="low_sleep", message=f"Son {n} kayıtta ortalama uyku {sleep:.1f} saat."))
        if social < LOW_SOCIAL:
            alerts.append(
                Alert(level="warning", code="low_social", message=f"Son {n} kayıtta sosyal etkileşim ortalaması {social:.1f}/10.")
            )
        if negative >= 3:
            alerts.append(
                Alert(
                    level="warning",
                    code="negative_mood",
                    message=f"Son {n} kaydın {negative} tanesinde zorlayıcı duygu durumu var.",
                )
            )
        if meltdowns >= 2:
            alerts.append(
                Alert(level="warning", code="meltdowns", message=f"Son {n} kayıtta {meltdowns} kez kriz (meltdown) yaşandı.")
            )

    if observation:
        if observation.sensory_sensitivity >= 7:
            alerts.append(
                Alert(
                    level="info",
                    code="sensory",
                    message=f"Duyusal hassasiyet yüksek gözlendi ({observation.sensory_sensitivity}/10).",
                )
            )
        if observation.eye_contact <= 3:
            alerts.append(
                Alert(level="info", code="eye_contact", message=f"Göz teması düşük gözlendi ({observation.eye_contact}/10).")
            )

    if screening and screening.risk_level in ("elevated", "high"):
        alerts.append(Alert(level="info", code="screening", message="Son tarama sonucu uzman değerlendirmesi öneriyor."))

    if next_visit and today <= next_visit <= today + timedelta(days=3):
        alerts.append(Alert(level="info", code="visit", message=f"Yaklaşan görüşme: {next_visit:%d.%m.%Y}."))

    return alerts


def _latest(db: Session, model, subject_id: int):
    return db.scalar(select(model).where(model.subject_id == subject_id).order_by(model.created_at.desc()).limit(1))


def _next_visit(db: Session, subject_id: int, today: date) -> date | None:
    return db.scalar(
        select(DoctorNote.next_visit)
        .where(DoctorNote.subject_id == subject_id, DoctorNote.next_visit >= today)
        .order_by(DoctorNote.next_visit)
        .limit(1)
    )


def compute(db: Session, subject: Subject, days: int = 30, today: date | None = None) -> Insights:
    today = today or date.today()
    logs = list(
        db.scalars(
            select(DailyLog)
            .where(DailyLog.subject_id == subject.id, DailyLog.log_date > today - timedelta(days=days))
            .order_by(DailyLog.log_date)
        )
    )
    recent = [log for log in logs if log.log_date > today - timedelta(days=RECENT_DAYS)]
    observation = _latest(db, ClinicalObservation, subject.id)
    screening = _latest(db, Screening, subject.id)
    next_visit = _next_visit(db, subject.id, today)
    all_dates = set(db.scalars(select(DailyLog.log_date).where(DailyLog.subject_id == subject.id)))

    stats = Stats(
        n_logs=len(logs),
        avg_sleep=_avg([log.sleep_hours for log in logs]),
        avg_social=_avg([log.social_interaction for log in logs]),
        meltdown_days=sum(log.meltdown for log in logs),
        mood_counts=dict(Counter(log.mood for log in logs)),
        streak=_streak(all_dates, today),
        logged_today=today in all_dates,
    )

    return Insights(
        stats=stats,
        series=[
            Point(
                date=log.log_date,
                sleep_hours=log.sleep_hours,
                social_interaction=log.social_interaction,
                mood=log.mood,
                meltdown=log.meltdown,
            )
            for log in logs
        ],
        alerts=_alerts(recent, observation, screening, next_visit, today),
        latest_screening=LatestScreening(
            id=screening.id,
            instrument=screening.instrument,
            risk_level=screening.risk_level,
            score=screening.score,
            created_at=screening.created_at.isoformat(),
        )
        if screening
        else None,
        next_visit=next_visit,
    )


def summarize(db: Session, subject: Subject) -> Summary:
    result = compute(db, subject, days=RECENT_DAYS)
    last_log = db.scalar(
        select(DailyLog.log_date).where(DailyLog.subject_id == subject.id).order_by(DailyLog.log_date.desc()).limit(1)
    )
    return Summary(
        latest_risk=result.latest_screening.risk_level if result.latest_screening else None,
        last_log_date=last_log,
        alert_count=sum(a.level != "info" for a in result.alerts),
        next_visit=result.next_visit,
    )
