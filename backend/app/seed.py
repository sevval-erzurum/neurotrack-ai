"""Demo verisi: dört rol için hesaplar ve 45 günlük gerçekçi takip geçmişi.

Çalıştırma (backend/ dizininden):
    python -m app.seed            # yalnızca boş veritabanına yazar
    python -m app.seed --reset    # demo hesaplarını silip yeniden oluşturur

Tüm demo hesaplarının şifresi: demo1234
"""

import argparse
import random
from dataclasses import asdict
from datetime import UTC, date, datetime, time, timedelta

from sqlalchemy import delete, or_, select

from app.core.db import SessionLocal
from app.core.security import hash_password
from app.ml import aq10, toddler
from app.models import (
    AuditEvent,
    CareTeamMember,
    ClinicalObservation,
    DailyLog,
    DoctorNote,
    DoctorStatus,
    Message,
    Notification,
    Role,
    Screening,
    Subject,
    SubjectKind,
    User,
)
from app.services import audit

PASSWORD = "demo1234"
DEMO_EMAILS = (
    "ebeveyn@example.com",
    "yetiskin@example.com",
    "doktor@example.com",
    "yonetici@example.com",
    "bekleyen.doktor@example.com",
)
DAYS = 45


def _at(day: date, hour: int) -> datetime:
    return datetime.combine(day, time(hour, 0), tzinfo=UTC)


def _months_ago(today: date, months: int) -> date:
    year, month = divmod(today.year * 12 + today.month - 1 - months, 12)
    return date(year, month + 1, min(today.day, 28))


def _logs(rng: random.Random, subject: Subject, author: User, today: date, profile: str) -> None:
    """Zorlu bir başlangıçtan iyileşmeye giden ya da son günlerde kötüleşen bir seyir üretir."""
    for offset in range(DAYS, -1, -1):
        if rng.random() < 0.12 and offset > 1:  # bazı günler kayıt girilmez
            continue
        progress = 1 - offset / DAYS
        if profile == "improving":
            sleep = rng.gauss(7.2 + 2.0 * progress, 0.7)
            social = rng.gauss(3.5 + 3.5 * progress, 1.1)
            p_negative, p_meltdown = 0.55 - 0.4 * progress, 0.35 - 0.3 * progress
        else:  # "recent_dip": iyi giderken son haftada uyku ve ruh hali bozulur
            dip = offset < 6
            sleep = rng.gauss(5.1 if dip else 7.4, 0.6)
            social = rng.gauss(3.0 if dip else 6.0, 1.0)
            p_negative, p_meltdown = (0.7, 0.3) if dip else (0.2, 0.05)

        mood = rng.choice(["anxious", "sad", "angry"]) if rng.random() < p_negative else rng.choice(["calm", "happy", "tired"])
        day = today - timedelta(days=offset)
        subject.daily_logs.append(
            DailyLog(
                author_id=author.id,
                log_date=day,
                mood=mood,
                sleep_hours=round(min(max(sleep, 3), 12) * 2) / 2,
                social_interaction=int(min(max(round(social), 0), 10)),
                meltdown=rng.random() < p_meltdown,
                note=None,
                created_at=_at(day, 20),
            )
        )


def _remove_demo(db) -> None:
    users = list(db.scalars(select(User).where(User.email.in_(DEMO_EMAILS))))
    user_ids = [u.id for u in users]
    subject_ids = [s.id for u in users for s in u.subjects]
    # Günlük yabancı anahtar kullanmaz; yeniden kullanılan ID'lerle eski kayıtlar karışmasın.
    db.execute(delete(AuditEvent).where(or_(AuditEvent.actor_id.in_(user_ids), AuditEvent.subject_id.in_(subject_ids))))
    for user in users:
        db.delete(user)
    db.commit()


def seed(reset: bool = False) -> None:
    rng = random.Random(7)
    today = date.today()

    with SessionLocal() as db:
        if reset:
            _remove_demo(db)
        elif db.scalar(select(User.id).where(User.email.in_(DEMO_EMAILS))):
            print("Demo hesapları zaten var. Yeniden oluşturmak için --reset kullanın.")
            return

        pw = hash_password(PASSWORD)
        parent = User(email="ebeveyn@example.com", full_name="Elif Demir", role=Role.PARENT, password_hash=pw)
        adult = User(email="yetiskin@example.com", full_name="Mert Aksoy", role=Role.ADULT, password_hash=pw)
        doctor = User(
            email="doktor@example.com",
            full_name="Dr. Zeynep Kaya",
            role=Role.DOCTOR,
            password_hash=pw,
            doctor_status=DoctorStatus.APPROVED,
            license_number="TR-2014-30871",
            institution="Ankara Çocuk Gelişim Merkezi",
            created_at=_at(today - timedelta(days=DAYS + 5), 9),
            reviewed_at=_at(today - timedelta(days=DAYS + 4), 11),
        )
        admin = User(email="yonetici@example.com", full_name="Sistem Yöneticisi", role=Role.ADMIN, password_hash=pw)
        # Onay akışını göstermek için başvurusu bekleyen bir doktor.
        applicant = User(
            email="bekleyen.doktor@example.com",
            full_name="Dr. Can Öztürk",
            role=Role.DOCTOR,
            password_hash=pw,
            doctor_status=DoctorStatus.PENDING,
            license_number="TR-2019-48213",
            institution="Özel Anka Çocuk Kliniği",
            created_at=_at(today - timedelta(days=1), 15),
        )
        db.add_all([parent, adult, doctor, admin, applicant])
        db.flush()
        doctor.reviewed_by_id = admin.id

        deniz = Subject(kind=SubjectKind.CHILD, name="Deniz", birth_date=_months_ago(today, 21), sex="male")
        ela = Subject(kind=SubjectKind.CHILD, name="Ela", birth_date=_months_ago(today, 62), sex="female")
        parent.subjects.extend([deniz, ela])
        mert = Subject(kind=SubjectKind.SELF, name=adult.full_name, birth_date=date(today.year - 27, 3, 14))
        adult.subjects.append(mert)
        db.flush()

        for subject in (deniz, mert):
            subject.care_team.append(CareTeamMember(doctor=doctor, created_at=_at(today - timedelta(days=DAYS), 10)))

        _logs(rng, deniz, parent, today, "improving")
        _logs(rng, ela, parent, today, "improving")
        _logs(rng, mert, adult, today, "recent_dip")

        # Q-CHAT taraması: model gerçekten çalıştırılır, açıklamalar gerçek model çıktısıdır.
        _, meta = toddler.load()
        answers = dict(zip([e["item"] for e in meta["items"]], [3, 1, 3, 3, 2, 3, 2, 2, 1, 2], strict=True))
        result = toddler.screen(answers)
        deniz.screenings.append(
            Screening(
                author_id=parent.id,
                instrument="qchat10",
                answers={str(k): v for k, v in answers.items()},
                score=result.probability,
                risk_level=result.risk_level,
                details={
                    "threshold": result.threshold,
                    "model_version": result.model_version,
                    "contributions": [asdict(c) for c in result.contributions],
                },
                created_at=_at(today - timedelta(days=40), 11),
            )
        )

        aq_answers = {1: 0, 2: 2, 3: 3, 4: 2, 5: 3, 6: 1, 7: 1, 8: 0, 9: 2, 10: 1}
        aq = aq10.score(aq_answers)
        mert.screenings.append(
            Screening(
                author_id=adult.id,
                instrument="aq10",
                answers={str(k): v for k, v in aq_answers.items()},
                score=aq.score,
                risk_level="elevated" if aq.refer else "low",
                details={"threshold": aq10.REFERRAL_THRESHOLD, "scored_items": aq.scored_items},
                created_at=_at(today - timedelta(days=38), 21),
            )
        )

        for days_ago, values in ((35, (8, 2, 3, 3)), (14, (7, 4, 4, 5)), (3, (6, 5, 5, 6))):
            sensory, eye, comm, routine = values
            deniz.observations.append(
                ClinicalObservation(
                    author_id=doctor.id if days_ago != 14 else parent.id,
                    sensory_sensitivity=sensory,
                    eye_contact=eye,
                    communication=comm,
                    routine_adaptation=routine,
                    eating_pattern="Seçici yeme, yeni yiyeceklere direnç",
                    therapy="Haftada 2 seans dil ve konuşma terapisi" if days_ago < 30 else None,
                    note="Ortam gürültülü olduğunda kulaklarını kapatıyor.",
                    created_at=_at(today - timedelta(days=days_ago), 15),
                )
            )

        deniz.notes.extend(
            [
                DoctorNote(
                    doctor_id=doctor.id,
                    body="Q-CHAT sonucu ve gözlem birlikte değerlendirildi. Ortak dikkat ve işaret etme "
                    "becerilerinde gecikme var. ADOS-2 değerlendirmesi planlandı.",
                    recommendation="Dil ve konuşma terapisine başlanması; günlük kayıtlara devam.",
                    next_visit=None,
                    created_at=_at(today - timedelta(days=34), 16),
                ),
                DoctorNote(
                    doctor_id=doctor.id,
                    body="Terapinin 4. haftası. Göz teması ve sosyal etkileşim skorlarında belirgin artış var. "
                    "Uyku düzeni oturmuş görünüyor.",
                    recommendation="Mevcut programı sürdürün. Duyusal mola alanını evde de deneyin.",
                    next_visit=today + timedelta(days=2),
                    created_at=_at(today - timedelta(days=3), 16),
                ),
            ]
        )
        mert.notes.append(
            DoctorNote(
                doctor_id=doctor.id,
                body="AQ-10 skoru eşiğin üzerinde. Kapsamlı yetişkin değerlendirmesi için randevu verildi.",
                recommendation="Uyku hijyeni; iş yerinde duyusal yükü azaltacak düzenlemeler.",
                next_visit=today + timedelta(days=9),
                created_at=_at(today - timedelta(days=30), 12),
            )
        )

        thread = [
            (parent, doctor, "Merhaba Zeynep Hanım, Deniz bu hafta kreşte ilk kez arkadaşına oyuncak uzattı!", 6),
            (doctor, parent, "Ne güzel bir gelişme! Kayıtlarda sosyal etkileşim artışını ben de görüyorum.", 6),
            (parent, doctor, "Perşembe randevusuna terapi raporunu da getirmeli miyim?", 1),
        ]
        for sender, recipient, body, days_ago in thread:
            sent = _at(today - timedelta(days=days_ago), 18)
            db.add(
                Message(
                    sender_id=sender.id,
                    recipient_id=recipient.id,
                    body=body,
                    created_at=sent,
                    read_at=sent if days_ago > 1 else None,
                )
            )

        db.add_all(
            [
                Notification(
                    user_id=doctor.id,
                    kind="message",
                    title="Elif Demir mesaj gönderdi",
                    body="Perşembe randevusuna terapi raporunu da getirmeli miyim?",
                    link=f"/messages?with={parent.id}",
                    created_at=_at(today - timedelta(days=1), 18),
                ),
                Notification(
                    user_id=parent.id,
                    kind="note",
                    title="Yeni doktor notu",
                    body="Dr. Zeynep Kaya, Deniz için not ekledi.",
                    link=f"/subjects/{deniz.id}",
                    created_at=_at(today - timedelta(days=3), 16),
                ),
            ]
        )
        db.add(
            Notification(
                user_id=admin.id,
                kind="doctor_application",
                title="Yeni doktor başvurusu",
                body="Dr. Can Öztürk (Özel Anka Çocuk Kliniği) onay bekliyor.",
                link="/admin/doctors",
                created_at=_at(today - timedelta(days=1), 15),
            )
        )

        # Erişim geçmişi: veri sahibinin "kim baktı" ekranı boş görünmesin.
        for days_ago, hour, action, subject in (
            (34, 15, "subject.view", deniz),
            (34, 15, "log.list", deniz),
            (34, 16, "note.create", deniz),
            (30, 12, "subject.view", mert),
            (30, 12, "note.create", mert),
            (3, 15, "subject.view", deniz),
            (3, 15, "insights.view", deniz),
            (3, 16, "note.create", deniz),
            (1, 9, "subject.view", mert),
            (1, 9, "log.list", mert),
        ):
            audit.record(
                db,
                action=action,
                status_code=201 if action.endswith("create") else 200,
                actor=doctor,
                subject_id=subject.id,
                created_at=_at(today - timedelta(days=days_ago), hour),
            )
        db.commit()

    print("Demo verisi oluşturuldu. Hesaplar (şifre: demo1234):")
    for email in DEMO_EMAILS:
        print(f"  {email}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--reset", action="store_true", help="Demo hesaplarını silip yeniden oluştur")
    seed(reset=parser.parse_args().reset)
