import os
from datetime import datetime, date, time, timedelta

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
import google.generativeai as genai

from app.database import engine, get_db
from app.models import (
    Base,
    User,
    Prediction,
    DailyLog,
    DoctorPatient,
    ClinicalFollowUp,
    Child,
    ChildDailyLog,
    DoctorChild,
    ChildClinicalFollowUp,
    DoctorNote,
    Notification,
    Message,
    MessageRequest,
    ChildAutismTest,
)
from app.security import hash_password, verify_password
from app.utils.predict import predict_autism


load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI()
Base.metadata.create_all(bind=engine)


# =========================================================
# Yardımcı Fonksiyonlar
# =========================================================

def create_notification(db: Session, user_id: int, title: str, message: str):
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        is_read=False,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def create_notification_if_not_exists(db: Session, user_id: int, title: str, message: str):
    existing = (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.title == title,
            Notification.message == message,
        )
        .first()
    )

    if existing:
        return existing

    return create_notification(db=db, user_id=user_id, title=title, message=message)


def parse_date_value(value):
    if value is None:
        return None

    if isinstance(value, date):
        return value

    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except Exception:
        return None


def are_users_connected_for_messaging(user1_id: int, user2_id: int, db: Session):
    accepted_request = (
        db.query(MessageRequest)
        .filter(
            or_(
                and_(MessageRequest.sender_id == user1_id, MessageRequest.receiver_id == user2_id),
                and_(MessageRequest.sender_id == user2_id, MessageRequest.receiver_id == user1_id),
            ),
            MessageRequest.status == "accepted",
        )
        .first()
    )
    return accepted_request is not None


def is_patient_assigned_to_doctor(patient_id: int, doctor_id: int, db: Session):
    relation = (
        db.query(DoctorPatient)
        .filter(
            DoctorPatient.patient_id == patient_id,
            DoctorPatient.doctor_id == doctor_id,
        )
        .first()
    )
    return relation is not None


def is_child_assigned_to_doctor(child_id: int, doctor_id: int, db: Session):
    relation = (
        db.query(DoctorChild)
        .filter(
            DoctorChild.child_id == child_id,
            DoctorChild.doctor_id == doctor_id,
        )
        .first()
    )
    return relation is not None


# =========================================================
# Pydantic Modelleri
# =========================================================

class AutismInput(BaseModel):
    A1_Score: int
    A2_Score: int
    A3_Score: int
    A4_Score: int
    A5_Score: int
    A6_Score: int
    A7_Score: int
    A8_Score: int
    A9_Score: int
    A10_Score: int
    age: int

class ChildAutismTestCreate(BaseModel):
    child_id: int
    A1_Score: int
    A2_Score: int
    A3_Score: int
    A4_Score: int
    A5_Score: int
    A6_Score: int
    A7_Score: int
    A8_Score: int
    A9_Score: int
    A10_Score: int
    age: int

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class DailyLogCreate(BaseModel):
    user_id: int
    mood: str
    sleep_hours: int
    social_interaction: int
    note: str


class ClinicalFollowUpCreate(BaseModel):
    user_id: int
    meltdown: str
    sensory_sensitivity: int
    eye_contact: int
    communication_willingness: int
    routine_reaction: int
    eating_pattern: str
    medication_therapy: str
    school_work_performance: int
    self_harm_risk: str
    note: str


class ChildCreate(BaseModel):
    parent_id: int
    name: str
    age: int
    gender: str


class ChildDailyLogCreate(BaseModel):
    child_id: int
    mood: str
    sleep_hours: int
    social_interaction: int
    note: str


class ChildClinicalFollowUpCreate(BaseModel):
    child_id: int
    meltdown: str
    sensory_sensitivity: int
    eye_contact: int
    communication_willingness: int
    routine_reaction: int
    eating_pattern: str
    medication_therapy: str
    note: str


class DoctorNoteCreate(BaseModel):
    doctor_id: int
    note: str
    recommendation: str
    next_visit_date: str
    child_id: int | None = None
    patient_id: int | None = None


class ChatMessage(BaseModel):
    user_id: int
    message: str
    role: str


class MessageCreate(BaseModel):
    sender_id: int
    receiver_id: int
    content: str


class SecureMessageRequestCreate(BaseModel):
    sender_id: int
    receiver_id: int


class SecureMessageCreate(BaseModel):
    sender_id: int
    receiver_id: int
    content: str


# =========================================================
# Temel Endpointler
# =========================================================

@app.get("/")
def home():
    return {"message": "Autism Prediction API çalışıyor"}


@app.post("/predict")
def predict(data: AutismInput):
    features = [
        data.A1_Score,
        data.A2_Score,
        data.A3_Score,
        data.A4_Score,
        data.A5_Score,
        data.A6_Score,
        data.A7_Score,
        data.A8_Score,
        data.A9_Score,
        data.A10_Score,
        data.age,
    ]

    result = predict_autism(features, data.age)

    return {
        "prediction": result,
        "message": "Otizm riski var" if result == 1 else "Otizm riski yok",
    }


@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Bu email zaten kayıtlı")

    if user.role not in ["adult", "parent", "doctor"]:
        raise HTTPException(status_code=400, detail="Rol adult, parent veya doctor olmalıdır")

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        password=hash_password(user.password),
        role=user.role,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Kullanıcı başarıyla oluşturuldu",
        "user_id": new_user.id,
        "email": new_user.email,
        "role": new_user.role,
    }


@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if not existing_user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    if not verify_password(user.password, existing_user.password):
        raise HTTPException(status_code=401, detail="Şifre yanlış")

    return {
        "message": "Giriş başarılı",
        "user_id": existing_user.id,
        "full_name": existing_user.full_name,
        "email": existing_user.email,
        "role": existing_user.role,
    }


# =========================================================
# Tahmin ve Günlük Kayıt
# =========================================================

@app.post("/predict-and-save")
def predict_and_save(data: AutismInput, user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    features = [
        data.A1_Score,
        data.A2_Score,
        data.A3_Score,
        data.A4_Score,
        data.A5_Score,
        data.A6_Score,
        data.A7_Score,
        data.A8_Score,
        data.A9_Score,
        data.A10_Score,
        data.age,
    ]

    result = predict_autism(features, data.age)

    new_prediction = Prediction(
        user_id=user_id,
        result=result,
        age=data.age,
    )

    db.add(new_prediction)
    db.commit()
    db.refresh(new_prediction)

    return {
        "message": "Tahmin başarıyla kaydedildi",
        "prediction_id": new_prediction.id,
        "user_id": user_id,
        "prediction": result,
        "age": data.age,
    }


@app.get("/my-predictions")
def my_predictions(user_id: int, db: Session = Depends(get_db)):
    records = (
        db.query(Prediction)
        .filter(Prediction.user_id == user_id)
        .order_by(Prediction.id.desc())
        .all()
    )

    return [
        {
            "id": r.id,
            "result": r.result,
            "age": r.age,
            "created_at": str(r.created_at) if r.created_at else None,
        }
        for r in records
    ]


@app.post("/daily-log")
def create_daily_log(data: DailyLogCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == data.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    new_log = DailyLog(
        user_id=data.user_id,
        mood=data.mood,
        sleep_hours=data.sleep_hours,
        social_interaction=data.social_interaction,
        note=data.note,
    )

    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    return {
        "message": "Günlük kayıt başarıyla eklendi",
        "log_id": new_log.id,
        "user_id": new_log.user_id,
        "mood": new_log.mood,
    }


@app.get("/my-daily-logs")
def get_daily_logs(user_id: int, db: Session = Depends(get_db)):
    records = (
        db.query(DailyLog)
        .filter(DailyLog.user_id == user_id)
        .order_by(DailyLog.id.desc())
        .all()
    )

    return [
        {
            "id": r.id,
            "user_id": r.user_id,
            "mood": r.mood,
            "sleep_hours": r.sleep_hours,
            "social_interaction": r.social_interaction,
            "note": r.note,
            "created_at": str(r.created_at) if r.created_at else None,
        }
        for r in records
    ]


# =========================================================
# Doktor - Yetişkin Hasta
# =========================================================

@app.post("/add-patient")
def add_patient(doctor_id: int, patient_id: int, db: Session = Depends(get_db)):
    doctor = db.query(User).filter(User.id == doctor_id).first()
    patient = db.query(User).filter(User.id == patient_id).first()

    if not doctor or doctor.role != "doctor":
        raise HTTPException(status_code=400, detail="Geçersiz doktor")

    if not patient:
        raise HTTPException(status_code=404, detail="Hasta bulunamadı")

    existing_relation = db.query(DoctorPatient).filter(
        DoctorPatient.doctor_id == doctor_id,
        DoctorPatient.patient_id == patient_id,
    ).first()

    if existing_relation:
        raise HTTPException(status_code=400, detail="Bu hasta zaten doktora eklenmiş")

    relation = DoctorPatient(
        doctor_id=doctor_id,
        patient_id=patient_id,
    )

    db.add(relation)
    db.commit()
    db.refresh(relation)

    create_notification(
        db=db,
        user_id=patient_id,
        title="Doktor eşleştirmesi",
        message=f"{doctor.full_name} sizi hasta listesine ekledi.",
    )

    return {
        "message": "Hasta doktora eklendi",
        "doctor_id": doctor_id,
        "patient_id": patient_id,
    }


@app.get("/my-patients")
def my_patients(doctor_id: int, db: Session = Depends(get_db)):
    relations = db.query(DoctorPatient).filter(
        DoctorPatient.doctor_id == doctor_id
    ).all()

    patients = []

    for relation in relations:
        user = db.query(User).filter(User.id == relation.patient_id).first()

        if user:
            patients.append({
                "id": user.id,
                "name": user.full_name,
                "email": user.email,
            })

    return patients


@app.get("/patient-details")
def patient_details(patient_id: int, db: Session = Depends(get_db)):
    predictions = db.query(Prediction).filter(Prediction.user_id == patient_id).all()
    logs = db.query(DailyLog).filter(DailyLog.user_id == patient_id).all()

    return {
        "predictions": [
            {
                "result": prediction.result,
                "age": prediction.age,
                "created_at": str(prediction.created_at) if prediction.created_at else None,
            }
            for prediction in predictions
        ],
        "daily_logs": [
            {
                "created_at": str(log.created_at) if log.created_at else None,
                "mood": log.mood,
                "sleep": log.sleep_hours,
                "sleep_hours": log.sleep_hours,
                "social": log.social_interaction,
                "social_interaction": log.social_interaction,
                "note": log.note,
            }
            for log in logs
        ],
    }


# =========================================================
# AI Destek ve Klinik Takip
# =========================================================

@app.get("/daily-log-analysis")
def daily_log_analysis(user_id: int, db: Session = Depends(get_db)):
    logs = db.query(DailyLog).filter(DailyLog.user_id == user_id).order_by(DailyLog.id.asc()).all()

    if len(logs) == 0:
        return {"message": "Henüz günlük kayıt yok."}

    latest_log = logs[-1]
    suggestions = []

    if latest_log.sleep_hours < 6:
        suggestions.append("Uyku süresi düşük görünüyor. Daha düzenli bir uyku takibi önerilir.")

    if latest_log.social_interaction < 4:
        suggestions.append("Sosyal etkileşim seviyesi düşük. Kısa ve güvenli sosyal aktiviteler destekleyici olabilir.")

    if latest_log.mood in ["üzgün", "kaygılı", "öfkeli"]:
        suggestions.append("Duygu durumu zorlayıcı görünüyor. Rahatlama egzersizleri, rutin planlama veya uzman desteği faydalı olabilir.")

    if len(suggestions) == 0:
        suggestions.append("Günlük kayıt genel olarak dengeli görünüyor. Mevcut rutinin sürdürülmesi önerilir.")

    return {
        "latest_mood": latest_log.mood,
        "sleep_hours": latest_log.sleep_hours,
        "social_interaction": latest_log.social_interaction,
        "note": latest_log.note,
        "suggestions": suggestions,
    }


@app.get("/patient-ai-summary")
def patient_ai_summary(patient_id: int, db: Session = Depends(get_db)):
    logs = db.query(DailyLog).filter(DailyLog.user_id == patient_id).all()
    predictions = db.query(Prediction).filter(Prediction.user_id == patient_id).all()

    if len(logs) == 0 and len(predictions) == 0:
        return {"message": "Bu hasta için henüz analiz edilecek veri yok."}

    summary = []

    if len(predictions) > 0:
        risk_count = sum(1 for prediction in predictions if prediction.result == 1)
        total_count = len(predictions)
        summary.append(
            f"Bu hasta için toplam {total_count} otizm tarama testi kaydı bulunmaktadır. "
            f"Bunların {risk_count} tanesinde model risk tespit etmiştir."
        )

    if len(logs) > 0:
        avg_sleep = sum(log.sleep_hours for log in logs) / len(logs)
        avg_social = sum(log.social_interaction for log in logs) / len(logs)

        mood_counts = {}
        for log in logs:
            mood_counts[log.mood] = mood_counts.get(log.mood, 0) + 1

        most_common_mood = max(mood_counts, key=mood_counts.get)

        summary.append(
            f"Günlük kayıtlar incelendiğinde ortalama uyku süresi {avg_sleep:.1f} saat, "
            f"ortalama sosyal etkileşim seviyesi {avg_social:.1f}/10 olarak görülmektedir. "
            f"En sık bildirilen duygu durumu '{most_common_mood}' olmuştur."
        )

        if avg_sleep < 6:
            summary.append("Uyku süresi düşük göründüğü için uyku düzeninin takip edilmesi önerilir.")

        if avg_social < 4:
            summary.append("Sosyal etkileşim seviyesi düşük olduğu için kontrollü sosyal aktiviteler desteklenebilir.")

        if most_common_mood in ["kaygılı", "üzgün", "öfkeli"]:
            summary.append("Duygu durumunda zorlanma görüldüğü için uzman değerlendirmesi veya destekleyici görüşme önerilebilir.")

    return {
        "patient_id": patient_id,
        "summary": summary,
    }


@app.post("/clinical-followup")
def create_clinical_followup(data: ClinicalFollowUpCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == data.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    new_record = ClinicalFollowUp(
        user_id=data.user_id,
        meltdown=data.meltdown,
        sensory_sensitivity=data.sensory_sensitivity,
        eye_contact=data.eye_contact,
        communication_willingness=data.communication_willingness,
        routine_reaction=data.routine_reaction,
        eating_pattern=data.eating_pattern,
        medication_therapy=data.medication_therapy,
        school_work_performance=data.school_work_performance,
        self_harm_risk=data.self_harm_risk,
        note=data.note,
    )

    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return {
        "message": "Klinik takip kaydı eklendi",
        "record_id": new_record.id,
        "user_id": new_record.user_id,
    }


@app.get("/clinical-followups")
def get_clinical_followups(user_id: int, db: Session = Depends(get_db)):
    records = db.query(ClinicalFollowUp).filter(
        ClinicalFollowUp.user_id == user_id
    ).order_by(ClinicalFollowUp.id.desc()).all()

    return [
        {
            "id": record.id,
            "user_id": record.user_id,
            "meltdown": record.meltdown,
            "sensory_sensitivity": record.sensory_sensitivity,
            "eye_contact": record.eye_contact,
            "communication_willingness": record.communication_willingness,
            "routine_reaction": record.routine_reaction,
            "eating_pattern": record.eating_pattern,
            "medication_therapy": record.medication_therapy,
            "school_work_performance": record.school_work_performance,
            "self_harm_risk": record.self_harm_risk,
            "note": record.note,
            "created_at": str(record.created_at) if record.created_at else None,
        }
        for record in records
    ]


# =========================================================
# Ebeveyn ve Çocuk Takibi
# =========================================================

@app.post("/children")
def create_child(data: ChildCreate, db: Session = Depends(get_db)):
    parent = db.query(User).filter(User.id == data.parent_id).first()

    if not parent:
        raise HTTPException(status_code=404, detail="Ebeveyn kullanıcı bulunamadı")

    if parent.role != "parent":
        raise HTTPException(status_code=400, detail="Bu kullanıcı ebeveyn rolünde değil")

    new_child = Child(
        parent_id=data.parent_id,
        name=data.name,
        age=data.age,
        gender=data.gender,
    )

    db.add(new_child)
    db.commit()
    db.refresh(new_child)

    return {
        "message": "Çocuk başarıyla eklendi",
        "child_id": new_child.id,
        "parent_id": new_child.parent_id,
        "name": new_child.name,
        "age": new_child.age,
        "gender": new_child.gender,
    }


@app.get("/children")
def get_children(parent_id: int, db: Session = Depends(get_db)):
    children = db.query(Child).filter(Child.parent_id == parent_id).order_by(Child.id.desc()).all()

    return [
        {
            "id": child.id,
            "parent_id": child.parent_id,
            "name": child.name,
            "age": child.age,
            "gender": child.gender,
            "created_at": str(child.created_at) if child.created_at else None,
        }
        for child in children
    ]


@app.post("/child-daily-log")
def create_child_daily_log(data: ChildDailyLogCreate, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == data.child_id).first()

    if not child:
        raise HTTPException(status_code=404, detail="Çocuk bulunamadı")

    new_log = ChildDailyLog(
        child_id=data.child_id,
        mood=data.mood,
        sleep_hours=data.sleep_hours,
        social_interaction=data.social_interaction,
        note=data.note,
    )

    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    return {
        "message": "Çocuk günlük kaydı başarıyla eklendi",
        "log_id": new_log.id,
        "child_id": new_log.child_id,
        "mood": new_log.mood,
    }


@app.get("/child-daily-logs")
def get_child_daily_logs(child_id: int, db: Session = Depends(get_db)):
    records = (
        db.query(ChildDailyLog)
        .filter(ChildDailyLog.child_id == child_id)
        .order_by(ChildDailyLog.id.desc())
        .all()
    )

    return [
        {
            "id": record.id,
            "child_id": record.child_id,
            "mood": record.mood,
            "sleep_hours": record.sleep_hours,
            "social_interaction": record.social_interaction,
            "note": record.note,
            "created_at": str(record.created_at) if record.created_at else None,
        }
        for record in records
    ]


@app.post("/add-child-patient")
def add_child_patient(doctor_id: int, child_id: int, db: Session = Depends(get_db)):
    doctor = db.query(User).filter(User.id == doctor_id).first()
    child = db.query(Child).filter(Child.id == child_id).first()

    if not doctor or doctor.role != "doctor":
        raise HTTPException(status_code=400, detail="Geçersiz doktor")

    if not child:
        raise HTTPException(status_code=404, detail="Çocuk bulunamadı")

    existing_relation = db.query(DoctorChild).filter(
        DoctorChild.doctor_id == doctor_id,
        DoctorChild.child_id == child_id,
    ).first()

    if existing_relation:
        raise HTTPException(status_code=400, detail="Bu çocuk zaten doktora eklenmiş")

    relation = DoctorChild(
        doctor_id=doctor_id,
        child_id=child_id,
    )

    db.add(relation)
    db.commit()
    db.refresh(relation)

    create_notification(
        db=db,
        user_id=child.parent_id,
        title="Çocuk doktor eşleştirmesi",
        message=f"{doctor.full_name}, {child.name} adlı çocuğu hasta listesine ekledi.",
    )

    return {
        "message": "Çocuk hasta doktora eklendi",
        "doctor_id": doctor_id,
        "child_id": child_id,
    }


@app.get("/my-child-patients")
def my_child_patients(doctor_id: int, db: Session = Depends(get_db)):
    relations = db.query(DoctorChild).filter(
        DoctorChild.doctor_id == doctor_id
    ).all()

    children = []

    for relation in relations:
        child = db.query(Child).filter(Child.id == relation.child_id).first()

        if child:
            parent = db.query(User).filter(User.id == child.parent_id).first()
            children.append({
                "id": child.id,
                "name": child.name,
                "age": child.age,
                "gender": child.gender,
                "parent_id": child.parent_id,
                "parent_name": parent.full_name if parent else None,
            })

    return children


@app.get("/child-patient-details")
def child_patient_details(child_id: int, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == child_id).first()

    if not child:
        raise HTTPException(status_code=404, detail="Çocuk bulunamadı")

    logs = db.query(ChildDailyLog).filter(ChildDailyLog.child_id == child_id).all()

    return {
        "child": {
            "id": child.id,
            "name": child.name,
            "age": child.age,
            "gender": child.gender,
            "parent_id": child.parent_id,
        },
        "daily_logs": [
            {
                "id": log.id,
                "mood": log.mood,
                "sleep_hours": log.sleep_hours,
                "social_interaction": log.social_interaction,
                "note": log.note,
                "created_at": str(log.created_at) if log.created_at else None,
            }
            for log in logs
        ],
    }


@app.post("/child-clinical-followup")
def create_child_clinical_followup(data: ChildClinicalFollowUpCreate, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == data.child_id).first()

    if not child:
        raise HTTPException(status_code=404, detail="Çocuk bulunamadı")

    new_record = ChildClinicalFollowUp(
        child_id=data.child_id,
        meltdown=data.meltdown,
        sensory_sensitivity=data.sensory_sensitivity,
        eye_contact=data.eye_contact,
        communication_willingness=data.communication_willingness,
        routine_reaction=data.routine_reaction,
        eating_pattern=data.eating_pattern,
        medication_therapy=data.medication_therapy,
        note=data.note,
    )

    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return {
        "message": "Çocuk klinik takip kaydı eklendi",
        "record_id": new_record.id,
        "child_id": new_record.child_id,
    }


@app.get("/child-clinical-followups")
def get_child_clinical_followups(child_id: int, db: Session = Depends(get_db)):
    records = (
        db.query(ChildClinicalFollowUp)
        .filter(ChildClinicalFollowUp.child_id == child_id)
        .order_by(ChildClinicalFollowUp.id.desc())
        .all()
    )

    return [
        {
            "id": record.id,
            "child_id": record.child_id,
            "meltdown": record.meltdown,
            "sensory_sensitivity": record.sensory_sensitivity,
            "eye_contact": record.eye_contact,
            "communication_willingness": record.communication_willingness,
            "routine_reaction": record.routine_reaction,
            "eating_pattern": record.eating_pattern,
            "medication_therapy": record.medication_therapy,
            "note": record.note,
            "created_at": str(record.created_at) if record.created_at else None,
        }
        for record in records
    ]


@app.get("/child-alerts")
def child_alerts(child_id: int, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == child_id).first()

    if not child:
        raise HTTPException(status_code=404, detail="Çocuk bulunamadı")

    daily_logs = db.query(ChildDailyLog).filter(ChildDailyLog.child_id == child_id).all()
    clinical_logs = db.query(ChildClinicalFollowUp).filter(ChildClinicalFollowUp.child_id == child_id).all()
    alerts = []

    if len(daily_logs) > 0:
        last_daily_logs = daily_logs[-5:]
        avg_sleep = sum(log.sleep_hours for log in last_daily_logs) / len(last_daily_logs)
        avg_social = sum(log.social_interaction for log in last_daily_logs) / len(last_daily_logs)
        negative_moods = ["üzgün", "kaygılı", "öfkeli"]
        negative_mood_count = sum(1 for log in last_daily_logs if log.mood in negative_moods)

        if avg_sleep < 6:
            alerts.append(f"Son {len(last_daily_logs)} günlük kayıtta ortalama uyku süresi düşük: {avg_sleep:.1f} saat.")
        if avg_social < 4:
            alerts.append(f"Son {len(last_daily_logs)} günlük kayıtta sosyal etkileşim seviyesi düşük: {avg_social:.1f}/10.")
        if negative_mood_count >= 3:
            alerts.append(f"Son {len(last_daily_logs)} günlük kayıtta olumsuz duygu durumu {negative_mood_count} kez gözlemlenmiş.")

    if len(clinical_logs) > 0:
        last_clinical_logs = clinical_logs[-5:]
        meltdown_count = sum(1 for log in last_clinical_logs if log.meltdown in ["Evet", "Kısmen"])
        avg_sensory = sum(log.sensory_sensitivity for log in last_clinical_logs) / len(last_clinical_logs)
        avg_eye_contact = sum(log.eye_contact for log in last_clinical_logs) / len(last_clinical_logs)

        if meltdown_count >= 2:
            alerts.append(f"Son {len(last_clinical_logs)} klinik kayıtta meltdown/kriz {meltdown_count} kez bildirilmiş.")
        if avg_sensory >= 7:
            alerts.append(f"Duyusal hassasiyet ortalaması yüksek görünüyor: {avg_sensory:.1f}/10.")
        if avg_eye_contact <= 3:
            alerts.append(f"Göz teması seviyesi düşük görünüyor: {avg_eye_contact:.1f}/10.")

    if len(alerts) == 0:
        alerts.append("Şu an belirgin bir takip uyarısı görünmüyor.")
    else:
        for alert in alerts:
            create_notification_if_not_exists(
                db=db,
                user_id=child.parent_id,
                title="Çocuk Takip Uyarısı",
                message=alert,
            )

    return {"child_id": child_id, "alerts": alerts}


# =========================================================
# Silme / İlişki Kaldırma Endpointleri
# =========================================================

@app.delete("/delete-child")
def delete_child(child_id: int, parent_id: int, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == child_id, Child.parent_id == parent_id).first()

    if not child:
        raise HTTPException(status_code=404, detail="Çocuk bulunamadı veya bu çocuğu silme yetkiniz yok.")

    db.query(ChildDailyLog).filter(ChildDailyLog.child_id == child_id).delete(synchronize_session=False)
    db.query(ChildClinicalFollowUp).filter(ChildClinicalFollowUp.child_id == child_id).delete(synchronize_session=False)
    db.query(DoctorNote).filter(DoctorNote.child_id == child_id).delete(synchronize_session=False)
    db.query(DoctorChild).filter(DoctorChild.child_id == child_id).delete(synchronize_session=False)

    db.delete(child)
    db.commit()

    return {"message": "Çocuk kaydı silindi."}


@app.delete("/remove-patient-from-doctor")
def remove_patient_from_doctor(doctor_id: int, patient_id: int, db: Session = Depends(get_db)):
    relation = db.query(DoctorPatient).filter(
        DoctorPatient.doctor_id == doctor_id,
        DoctorPatient.patient_id == patient_id,
    ).first()

    if not relation:
        raise HTTPException(status_code=404, detail="Bu hasta zaten doktor listenizde bulunmuyor.")

    db.delete(relation)
    db.commit()

    return {"message": "Hasta doktor listesinden çıkarıldı."}


@app.delete("/remove-child-patient-from-doctor")
def remove_child_patient_from_doctor(doctor_id: int, child_id: int, db: Session = Depends(get_db)):
    relation = db.query(DoctorChild).filter(
        DoctorChild.doctor_id == doctor_id,
        DoctorChild.child_id == child_id,
    ).first()

    if not relation:
        raise HTTPException(status_code=404, detail="Bu çocuk hasta zaten doktor listenizde bulunmuyor.")

    db.delete(relation)
    db.commit()

    return {"message": "Çocuk hasta doktor listesinden çıkarıldı."}


# =========================================================
# Doktor Notları ve Bildirimler
# =========================================================

@app.post("/doctor-note")
def create_doctor_note(data: DoctorNoteCreate, db: Session = Depends(get_db)):
    doctor = db.query(User).filter(User.id == data.doctor_id).first()

    if not doctor or doctor.role != "doctor":
        raise HTTPException(status_code=400, detail="Geçersiz doktor")

    if not data.patient_id and not data.child_id:
        raise HTTPException(status_code=400, detail="patient_id veya child_id gönderilmelidir")

    target_user_id = None
    target_name = "Hasta"

    if data.patient_id:
        patient = db.query(User).filter(User.id == data.patient_id).first()

        if not patient:
            raise HTTPException(status_code=404, detail="Hasta bulunamadı")

        if not is_patient_assigned_to_doctor(patient.id, doctor.id, db):
            raise HTTPException(status_code=403, detail="Bu hasta doktora atanmış görünmüyor")

        target_user_id = patient.id
        target_name = patient.full_name

    if data.child_id:
        child = db.query(Child).filter(Child.id == data.child_id).first()

        if not child:
            raise HTTPException(status_code=404, detail="Çocuk bulunamadı")

        if not is_child_assigned_to_doctor(child.id, doctor.id, db):
            raise HTTPException(status_code=403, detail="Bu çocuk hasta doktora atanmış görünmüyor")

        target_user_id = child.parent_id
        target_name = child.name

    new_note = DoctorNote(
        doctor_id=data.doctor_id,
        child_id=data.child_id,
        patient_id=data.patient_id,
        note=data.note,
        recommendation=data.recommendation,
        next_visit_date=data.next_visit_date,
    )

    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    if target_user_id:
        create_notification(
            db=db,
            user_id=target_user_id,
            title="Yeni doktor notu",
            message=f"{doctor.full_name} tarafından {target_name} için yeni doktor notu eklendi. Sonraki görüşme: {data.next_visit_date}",
        )

    create_notification(
        db=db,
        user_id=data.doctor_id,
        title="Doktor notu kaydedildi",
        message=f"{target_name} için doktor notu başarıyla kaydedildi.",
    )

    return {
        "message": "Doktor notu eklendi ve bildirim oluşturuldu",
        "note_id": new_note.id,
        "target_user_id": target_user_id,
    }


@app.get("/doctor-notes")
def get_doctor_notes(child_id: int | None = None, patient_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(DoctorNote)

    if child_id:
        query = query.filter(DoctorNote.child_id == child_id)

    if patient_id:
        query = query.filter(DoctorNote.patient_id == patient_id)

    notes = query.order_by(DoctorNote.id.desc()).all()

    return [
        {
            "id": note.id,
            "doctor_id": note.doctor_id,
            "child_id": note.child_id,
            "patient_id": note.patient_id,
            "note": note.note,
            "recommendation": note.recommendation,
            "next_visit_date": note.next_visit_date,
            "created_at": str(note.created_at) if note.created_at else None,
        }
        for note in notes
    ]


@app.get("/my-doctor-notes")
def my_doctor_notes(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")

    notes = []

    if user.role == "adult":
        records = db.query(DoctorNote).filter(
            DoctorNote.patient_id == user_id
        ).order_by(DoctorNote.id.desc()).all()

        for note in records:
            doctor = db.query(User).filter(User.id == note.doctor_id).first()
            notes.append({
                "id": note.id,
                "doctor_name": doctor.full_name if doctor else "Doktor",
                "target_name": user.full_name,
                "target_type": "adult",
                "note": note.note,
                "recommendation": note.recommendation,
                "next_visit_date": note.next_visit_date,
                "created_at": str(note.created_at) if note.created_at else None,
            })

    elif user.role == "parent":
        children = db.query(Child).filter(Child.parent_id == user_id).all()
        child_ids = [child.id for child in children]

        if child_ids:
            records = db.query(DoctorNote).filter(
                DoctorNote.child_id.in_(child_ids)
            ).order_by(DoctorNote.id.desc()).all()

            for note in records:
                doctor = db.query(User).filter(User.id == note.doctor_id).first()
                child = db.query(Child).filter(Child.id == note.child_id).first()
                notes.append({
                    "id": note.id,
                    "doctor_name": doctor.full_name if doctor else "Doktor",
                    "target_name": child.name if child else "Çocuk",
                    "target_type": "child",
                    "note": note.note,
                    "recommendation": note.recommendation,
                    "next_visit_date": note.next_visit_date,
                    "created_at": str(note.created_at) if note.created_at else None,
                })

    elif user.role == "doctor":
        records = db.query(DoctorNote).filter(
            DoctorNote.doctor_id == user_id
        ).order_by(DoctorNote.id.desc()).all()

        for note in records:
            target_name = "Hasta"
            target_type = "adult"

            if note.patient_id:
                patient = db.query(User).filter(User.id == note.patient_id).first()
                target_name = patient.full_name if patient else "Hasta"

            if note.child_id:
                child = db.query(Child).filter(Child.id == note.child_id).first()
                target_name = child.name if child else "Çocuk"
                target_type = "child"

            notes.append({
                "id": note.id,
                "doctor_name": user.full_name,
                "target_name": target_name,
                "target_type": target_type,
                "note": note.note,
                "recommendation": note.recommendation,
                "next_visit_date": note.next_visit_date,
                "created_at": str(note.created_at) if note.created_at else None,
            })

    return notes


@app.get("/notifications")
def get_notifications(user_id: int, db: Session = Depends(get_db)):
    try:
        generate_smart_notifications_for_user(user_id=user_id, db=db)
    except Exception:
        pass

    records = db.query(Notification).filter(
        Notification.user_id == user_id
    ).order_by(Notification.id.desc()).all()

    return [
        {
            "id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "is_read": notification.is_read,
            "created_at": str(notification.created_at) if notification.created_at else None,
        }
        for notification in records
    ]


@app.post("/mark-notification-read")
def mark_notification_read(notification_id: int, db: Session = Depends(get_db)):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Bildirim bulunamadı")

    notification.is_read = True
    db.commit()

    return {"message": "Bildirim okundu olarak işaretlendi"}


# =========================================================
# Chatbot ve AI Analizleri
# =========================================================

@app.post("/chatbot")
def chatbot(data: ChatMessage):
    message = data.message.lower()
    fallback_response = []

    if "kaygı" in message or "kaygılı" in message or "anksiyete" in message:
        fallback_response.append(
            "Mesajında kaygı ile ilgili bir ifade görüyorum. Kısa nefes egzersizleri, sakin bir rutin ve güvende hissettiren aktiviteler yardımcı olabilir."
        )

    if "uyuyamıyorum" in message or "uyku" in message or "uyuyamadım" in message:
        fallback_response.append(
            "Uyku ile ilgili zorlanma fark ediliyor. Ekran süresini azaltmak, düzenli uyku saati belirlemek ve sakinleştirici bir gece rutini oluşturmak faydalı olabilir."
        )

    if "üzgün" in message or "mutsuz" in message:
        fallback_response.append(
            "Üzgün hissettiğini anlıyorum. Günlük duygu takibi yapmak ve bu durumu güvendiğin biriyle paylaşmak destekleyici olabilir."
        )

    if "öfke" in message or "öfkeli" in message or "sinir" in message:
        fallback_response.append(
            "Öfke veya sinirlilik yaşandığında kısa mola vermek, ortamı sakinleştirmek ve tetikleyicileri not etmek faydalı olabilir."
        )

    if "kriz" in message or "meltdown" in message:
        fallback_response.append(
            "Kriz veya meltdown durumlarında çevresel uyaranları azaltmak, kişiye güvenli alan sağlamak ve sonrasında tetikleyici durumu kaydetmek önemlidir."
        )

    if "duyusal" in message or "ses" in message or "ışık" in message or "kalabalık" in message:
        fallback_response.append(
            "Duyusal hassasiyet belirtileri olabilir. Gürültü, ışık veya kalabalık gibi tetikleyicileri takip etmek ve gerektiğinde düşük uyaranlı ortamlar oluşturmak faydalı olabilir."
        )

    if len(fallback_response) == 0:
        fallback_response.append(
            "Mesajını aldım. Bu sistem destekleyici öneriler sunar ancak tanı koymaz. Duygu, uyku, sosyal etkileşim ve günlük notlarını düzenli takip etmen faydalı olabilir."
        )

    fallback_response.append(
        "Not: Bu yanıt tıbbi tanı veya tedavi yerine geçmez. Gerekli durumlarda bir uzmana başvurulmalıdır."
    )

    try:
        if not GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY bulunamadı")

        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""
Kullanıcı rolü: {data.role}

Eğer rol:
- adult → bireysel destek ver
- parent → ebeveyne çocuk hakkında rehberlik ver
- doctor → klinik ve teknik yorum yap

Kurallar:
- Tanı koyma
- Tıbbi kesinlik verme
- Empatik ol
- Türkçe yaz
- Kısa ve anlaşılır ol

Kullanıcı mesajı:
{data.message}
"""

        response = model.generate_content(prompt)

        return {
            "user_id": data.user_id,
            "user_message": data.message,
            "bot_response": response.text,
            "ai_source": "Gemini",
        }

    except Exception as error:
        return {
            "user_id": data.user_id,
            "user_message": data.message,
            "bot_response": " ".join(fallback_response),
            "ai_source": "Fallback",
            "gemini_error": str(error),
        }


@app.get("/progress-score")
def progress_score(user_id: int, db: Session = Depends(get_db)):
    logs = db.query(DailyLog).filter(
        DailyLog.user_id == user_id
    ).order_by(DailyLog.created_at.desc()).limit(10).all()

    if len(logs) == 0:
        return {"message": "Yeterli veri yok"}

    text_data = ""
    for log in logs:
        text_data += f"""
        Duygu: {log.mood}
        Uyku: {log.sleep_hours}
        Sosyal: {log.social_interaction}
        """

    try:
        if not GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY bulunamadı")

        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""
Aşağıdaki kullanıcı verilerini analiz et:

{text_data}

Şunları üret:
1. 0-100 arası gelişim skoru
2. Genel durum: iyi / orta / kötü
3. Kısa yorum
4. Risk var mı?

Kısa ve net yaz.
Türkçe yaz.
"""
        response = model.generate_content(prompt)
        return {"analysis": response.text}

    except Exception:
        return {"analysis": "AI analiz yapılamadı, temel değerlendirme yapılmalı."}


@app.get("/risk-alert")
def risk_alert(user_id: int, db: Session = Depends(get_db)):
    logs = db.query(DailyLog).filter(DailyLog.user_id == user_id).order_by(DailyLog.id.desc()).limit(3).all()

    if len(logs) < 3:
        return {"risk": False, "message": "Yeterli veri yok"}

    risk_count = 0

    for log in logs:
        if (
            log.mood in ["üzgün", "kaygılı", "öfkeli"]
            or log.sleep_hours < 5
            or log.social_interaction < 3
        ):
            risk_count += 1

    if risk_count >= 3:
        return {"risk": True, "message": "Son günlerde riskli durum tespit edildi"}

    return {"risk": False, "message": "Normal"}


# =========================================================
# Mesajlaşma
# =========================================================

@app.post("/send-message")
def send_message(message: MessageCreate, db: Session = Depends(get_db)):
    sender = db.query(User).filter(User.id == message.sender_id).first()
    receiver = db.query(User).filter(User.id == message.receiver_id).first()

    if not sender:
        raise HTTPException(status_code=404, detail="Gönderen kullanıcı bulunamadı.")
    if not receiver:
        raise HTTPException(status_code=404, detail="Alıcı kullanıcı bulunamadı.")
    if not message.content.strip():
        raise HTTPException(status_code=400, detail="Mesaj boş olamaz.")

    new_message = Message(
        sender_id=message.sender_id,
        receiver_id=message.receiver_id,
        content=message.content,
        is_read=False,
    )

    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    create_notification(
        db=db,
        user_id=receiver.id,
        title="Yeni mesaj",
        message=f"{sender.full_name} size mesaj gönderdi: {message.content[:80]}",
    )

    return {
        "message": "Mesaj gönderildi.",
        "id": new_message.id,
        "sender_id": new_message.sender_id,
        "receiver_id": new_message.receiver_id,
        "content": new_message.content,
        "is_read": new_message.is_read,
        "created_at": str(new_message.created_at) if new_message.created_at else None,
    }


@app.get("/my-messages")
def get_my_messages(user_id: int, db: Session = Depends(get_db)):
    messages = (
        db.query(Message)
        .filter(or_(Message.sender_id == user_id, Message.receiver_id == user_id))
        .order_by(Message.id.desc())
        .all()
    )

    result = []

    for msg in messages:
        sender = db.query(User).filter(User.id == msg.sender_id).first()
        receiver = db.query(User).filter(User.id == msg.receiver_id).first()

        result.append({
            "id": msg.id,
            "sender_id": msg.sender_id,
            "sender_name": sender.full_name if sender else "-",
            "sender_role": sender.role if sender else "-",
            "receiver_id": msg.receiver_id,
            "receiver_name": receiver.full_name if receiver else "-",
            "receiver_role": receiver.role if receiver else "-",
            "content": msg.content,
            "is_read": msg.is_read,
            "created_at": str(msg.created_at) if msg.created_at else None,
        })

    return result


@app.get("/conversation")
def get_conversation(user1_id: int, user2_id: int, db: Session = Depends(get_db)):
    messages = (
        db.query(Message)
        .filter(
            or_(
                and_(Message.sender_id == user1_id, Message.receiver_id == user2_id),
                and_(Message.sender_id == user2_id, Message.receiver_id == user1_id),
            )
        )
        .order_by(Message.id.asc())
        .all()
    )

    result = []

    for msg in messages:
        sender = db.query(User).filter(User.id == msg.sender_id).first()
        receiver = db.query(User).filter(User.id == msg.receiver_id).first()

        result.append({
            "id": msg.id,
            "sender_id": msg.sender_id,
            "sender_name": sender.full_name if sender else "-",
            "sender_role": sender.role if sender else "-",
            "receiver_id": msg.receiver_id,
            "receiver_name": receiver.full_name if receiver else "-",
            "receiver_role": receiver.role if receiver else "-",
            "content": msg.content,
            "is_read": msg.is_read,
            "created_at": str(msg.created_at) if msg.created_at else None,
        })

    return result


@app.post("/mark-message-read")
def mark_message_read(message_id: int, db: Session = Depends(get_db)):
    message = db.query(Message).filter(Message.id == message_id).first()

    if not message:
        raise HTTPException(status_code=404, detail="Mesaj bulunamadı.")

    message.is_read = True
    db.commit()

    return {"message": "Mesaj okundu olarak işaretlendi."}


@app.get("/available-doctors-for-message")
def available_doctors_for_message(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")

    if user.role == "doctor":
        return []

    relations = db.query(DoctorPatient).filter(DoctorPatient.patient_id == user_id).all()
    doctors = []

    for relation in relations:
        doctor = db.query(User).filter(User.id == relation.doctor_id).first()

        if doctor:
            existing_request = (
                db.query(MessageRequest)
                .filter(
                    or_(
                        and_(MessageRequest.sender_id == user_id, MessageRequest.receiver_id == doctor.id),
                        and_(MessageRequest.sender_id == doctor.id, MessageRequest.receiver_id == user_id),
                    )
                )
                .first()
            )

            doctors.append({
                "user_id": doctor.id,
                "full_name": doctor.full_name,
                "email": doctor.email,
                "role": doctor.role,
                "request_status": existing_request.status if existing_request else "none",
            })

    return doctors


@app.post("/send-message-request")
def send_secure_message_request(request_data: SecureMessageRequestCreate, db: Session = Depends(get_db)):
    sender = db.query(User).filter(User.id == request_data.sender_id).first()
    receiver = db.query(User).filter(User.id == request_data.receiver_id).first()

    if not sender:
        raise HTTPException(status_code=404, detail="Gönderen kullanıcı bulunamadı.")
    if not receiver:
        raise HTTPException(status_code=404, detail="Alıcı kullanıcı bulunamadı.")
    if receiver.role != "doctor":
        raise HTTPException(status_code=400, detail="Mesaj isteği sadece doktora gönderilebilir.")
    if sender.role == "doctor":
        raise HTTPException(status_code=400, detail="Doktor mesaj isteği gönderemez. Hastadan gelen isteği kabul etmelidir.")
    if not is_patient_assigned_to_doctor(sender.id, receiver.id, db):
        raise HTTPException(status_code=403, detail="Bu doktora mesaj isteği gönderemezsiniz. Sadece size atanmış doktora istek gönderebilirsiniz.")

    existing_request = (
        db.query(MessageRequest)
        .filter(
            or_(
                and_(MessageRequest.sender_id == sender.id, MessageRequest.receiver_id == receiver.id),
                and_(MessageRequest.sender_id == receiver.id, MessageRequest.receiver_id == sender.id),
            )
        )
        .first()
    )

    if existing_request:
        return {
            "message": "Bu doktor ile zaten mesaj isteği kaydı var.",
            "request_id": existing_request.id,
            "status": existing_request.status,
        }

    new_request = MessageRequest(sender_id=sender.id, receiver_id=receiver.id, status="pending")
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    create_notification(
        db=db,
        user_id=receiver.id,
        title="Yeni sohbet isteği",
        message=f"{sender.full_name} sizinle mesajlaşmak için istek gönderdi.",
    )

    return {
        "message": "Mesaj isteği doktora gönderildi.",
        "request_id": new_request.id,
        "status": new_request.status,
    }


@app.get("/message-requests")
def get_message_requests(user_id: int, db: Session = Depends(get_db)):
    requests = (
        db.query(MessageRequest)
        .filter(or_(MessageRequest.sender_id == user_id, MessageRequest.receiver_id == user_id))
        .order_by(MessageRequest.id.desc())
        .all()
    )

    result = []

    for req in requests:
        sender = db.query(User).filter(User.id == req.sender_id).first()
        receiver = db.query(User).filter(User.id == req.receiver_id).first()

        result.append({
            "id": req.id,
            "sender_id": req.sender_id,
            "sender_name": sender.full_name if sender else "-",
            "sender_role": sender.role if sender else "-",
            "receiver_id": req.receiver_id,
            "receiver_name": receiver.full_name if receiver else "-",
            "receiver_role": receiver.role if receiver else "-",
            "status": req.status,
            "created_at": str(req.created_at) if req.created_at else None,
        })

    return result


@app.post("/respond-message-request")
def respond_message_request(request_id: int, status: str, user_id: int, db: Session = Depends(get_db)):
    if status not in ["accepted", "rejected"]:
        raise HTTPException(status_code=400, detail="Status accepted veya rejected olmalı.")

    request_obj = db.query(MessageRequest).filter(MessageRequest.id == request_id).first()

    if not request_obj:
        raise HTTPException(status_code=404, detail="Mesaj isteği bulunamadı.")
    if request_obj.receiver_id != user_id:
        raise HTTPException(status_code=403, detail="Bu isteği sadece alıcı doktor cevaplayabilir.")

    receiver = db.query(User).filter(User.id == user_id).first()
    sender = db.query(User).filter(User.id == request_obj.sender_id).first()

    if not receiver or receiver.role != "doctor":
        raise HTTPException(status_code=403, detail="Mesaj isteğini sadece doktor kabul edebilir.")

    request_obj.status = status
    db.commit()

    if sender:
        create_notification(
            db=db,
            user_id=sender.id,
            title="Sohbet isteği kabul edildi" if status == "accepted" else "Sohbet isteği reddedildi",
            message=f"{receiver.full_name} mesajlaşma isteğinizi {status} olarak güncelledi.",
        )

    return {
        "message": f"Mesaj isteği {status} olarak güncellendi.",
        "request_id": request_obj.id,
        "status": request_obj.status,
    }


@app.get("/message-contacts")
def get_message_contacts(user_id: int, db: Session = Depends(get_db)):
    accepted_requests = (
        db.query(MessageRequest)
        .filter(or_(MessageRequest.sender_id == user_id, MessageRequest.receiver_id == user_id))
        .filter(MessageRequest.status == "accepted")
        .all()
    )

    contacts = []

    for req in accepted_requests:
        other_user_id = req.receiver_id if req.sender_id == user_id else req.sender_id
        other_user = db.query(User).filter(User.id == other_user_id).first()

        if other_user:
            last_message = (
                db.query(Message)
                .filter(
                    or_(
                        and_(Message.sender_id == user_id, Message.receiver_id == other_user_id),
                        and_(Message.sender_id == other_user_id, Message.receiver_id == user_id),
                    )
                )
                .order_by(Message.id.desc())
                .first()
            )

            contacts.append({
                "user_id": other_user.id,
                "full_name": other_user.full_name,
                "email": other_user.email,
                "role": other_user.role,
                "last_message": last_message.content if last_message else "Henüz mesaj yok.",
                "last_date": str(last_message.created_at) if last_message and last_message.created_at else None,
            })

    return contacts


@app.post("/secure-send-message")
def secure_send_message(message: SecureMessageCreate, db: Session = Depends(get_db)):
    sender = db.query(User).filter(User.id == message.sender_id).first()
    receiver = db.query(User).filter(User.id == message.receiver_id).first()

    if not sender:
        raise HTTPException(status_code=404, detail="Gönderen kullanıcı bulunamadı.")
    if not receiver:
        raise HTTPException(status_code=404, detail="Alıcı kullanıcı bulunamadı.")
    if not are_users_connected_for_messaging(sender.id, receiver.id, db):
        raise HTTPException(status_code=403, detail="Bu kullanıcı ile mesajlaşma izniniz yok. Önce doktor mesaj isteğini kabul etmelidir.")
    if not message.content.strip():
        raise HTTPException(status_code=400, detail="Mesaj boş olamaz.")

    new_message = Message(sender_id=sender.id, receiver_id=receiver.id, content=message.content, is_read=False)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    create_notification(
        db=db,
        user_id=receiver.id,
        title="Yeni mesaj",
        message=f"{sender.full_name} size mesaj gönderdi: {message.content[:80]}",
    )

    return {
        "message": "Mesaj gönderildi.",
        "id": new_message.id,
        "sender_id": new_message.sender_id,
        "receiver_id": new_message.receiver_id,
        "content": new_message.content,
        "is_read": new_message.is_read,
        "created_at": str(new_message.created_at) if new_message.created_at else None,
    }


@app.get("/secure-conversation")
def secure_conversation(user1_id: int, user2_id: int, db: Session = Depends(get_db)):
    if not are_users_connected_for_messaging(user1_id, user2_id, db):
        raise HTTPException(status_code=403, detail="Bu kullanıcı ile konuşma izniniz yok.")

    messages = (
        db.query(Message)
        .filter(
            or_(
                and_(Message.sender_id == user1_id, Message.receiver_id == user2_id),
                and_(Message.sender_id == user2_id, Message.receiver_id == user1_id),
            )
        )
        .order_by(Message.id.asc())
        .all()
    )

    result = []

    for msg in messages:
        sender = db.query(User).filter(User.id == msg.sender_id).first()
        receiver = db.query(User).filter(User.id == msg.receiver_id).first()

        if msg.receiver_id == user1_id and not msg.is_read:
            msg.is_read = True

        result.append({
            "id": msg.id,
            "sender_id": msg.sender_id,
            "sender_name": sender.full_name if sender else "-",
            "sender_role": sender.role if sender else "-",
            "receiver_id": msg.receiver_id,
            "receiver_name": receiver.full_name if receiver else "-",
            "receiver_role": receiver.role if receiver else "-",
            "content": msg.content,
            "is_read": msg.is_read,
            "created_at": str(msg.created_at) if msg.created_at else None,
        })

    db.commit()
    return result


# =========================================================
# Akıllı Bildirimler
# =========================================================

def generate_smart_notifications_for_user(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")

    today = date.today()
    start_of_day = datetime.combine(today, time.min)
    end_of_day = datetime.combine(today, time.max)
    upcoming_limit = today + timedelta(days=3)

    unread_messages = db.query(Message).filter(Message.receiver_id == user_id, Message.is_read == False).all()

    for msg in unread_messages:
        sender = db.query(User).filter(User.id == msg.sender_id).first()
        sender_name = sender.full_name if sender else "Bilinmeyen kullanıcı"
        create_notification_if_not_exists(
            db,
            user_id,
            "Yeni mesaj",
            f"{sender_name} size mesaj gönderdi: {msg.content[:80]}",
        )

    if user.role == "doctor":
        pending_requests = db.query(MessageRequest).filter(MessageRequest.receiver_id == user_id, MessageRequest.status == "pending").all()
        for req in pending_requests:
            sender = db.query(User).filter(User.id == req.sender_id).first()
            sender_name = sender.full_name if sender else "Hasta"
            create_notification_if_not_exists(
                db,
                user_id,
                "Yeni sohbet isteği",
                f"{sender_name} sizinle mesajlaşmak için istek gönderdi.",
            )

    if user.role != "doctor":
        my_requests = db.query(MessageRequest).filter(MessageRequest.sender_id == user_id).all()
        for req in my_requests:
            doctor = db.query(User).filter(User.id == req.receiver_id).first()
            doctor_name = doctor.full_name if doctor else "Doktor"
            if req.status == "accepted":
                create_notification_if_not_exists(
                    db,
                    user_id,
                    "Sohbet isteği kabul edildi",
                    f"{doctor_name} mesajlaşma isteğinizi kabul etti. Artık sohbet başlatabilirsiniz.",
                )
            if req.status == "rejected":
                create_notification_if_not_exists(
                    db,
                    user_id,
                    "Sohbet isteği reddedildi",
                    f"{doctor_name} mesajlaşma isteğinizi reddetti.",
                )

    if user.role == "adult":
        today_log = db.query(DailyLog).filter(
            DailyLog.user_id == user_id,
            DailyLog.created_at >= start_of_day,
            DailyLog.created_at <= end_of_day,
        ).first()
        if not today_log:
            create_notification_if_not_exists(
                db,
                user_id,
                "Günlük kayıt hatırlatması",
                f"{today.strftime('%Y-%m-%d')} tarihli günlük kaydınızı henüz eklemediniz.",
            )

    if user.role == "parent":
        children = db.query(Child).filter(Child.parent_id == user_id).all()
        for child in children:
            today_child_log = db.query(ChildDailyLog).filter(
                ChildDailyLog.child_id == child.id,
                ChildDailyLog.created_at >= start_of_day,
                ChildDailyLog.created_at <= end_of_day,
            ).first()
            if not today_child_log:
                create_notification_if_not_exists(
                    db,
                    user_id,
                    "Çocuk günlük kayıt hatırlatması",
                    f"{child.name} için {today.strftime('%Y-%m-%d')} tarihli günlük kayıt henüz eklenmedi.",
                )

    if user.role == "adult":
        notes = db.query(DoctorNote).filter(DoctorNote.patient_id == user_id).all()
        for note in notes:
            visit_date = parse_date_value(note.next_visit_date)
            if visit_date and today <= visit_date <= upcoming_limit:
                create_notification_if_not_exists(
                    db,
                    user_id,
                    "Yaklaşan görüşme",
                    f"{visit_date.strftime('%Y-%m-%d')} tarihinde doktor görüşmeniz bulunmaktadır.",
                )

    if user.role == "parent":
        children = db.query(Child).filter(Child.parent_id == user_id).all()
        child_ids = [child.id for child in children]
        if child_ids:
            notes = db.query(DoctorNote).filter(DoctorNote.child_id.in_(child_ids)).all()
            for note in notes:
                visit_date = parse_date_value(note.next_visit_date)
                child = db.query(Child).filter(Child.id == note.child_id).first()
                child_name = child.name if child else "Çocuk"
                if visit_date and today <= visit_date <= upcoming_limit:
                    create_notification_if_not_exists(
                        db,
                        user_id,
                        "Yaklaşan çocuk görüşmesi",
                        f"{child_name} için {visit_date.strftime('%Y-%m-%d')} tarihinde doktor görüşmesi bulunmaktadır.",
                    )

    if user.role == "doctor":
        notes = db.query(DoctorNote).filter(DoctorNote.doctor_id == user_id).all()
        for note in notes:
            visit_date = parse_date_value(note.next_visit_date)
            if visit_date and today <= visit_date <= upcoming_limit:
                if note.patient_id:
                    patient = db.query(User).filter(User.id == note.patient_id).first()
                    patient_name = patient.full_name if patient else "Hasta"
                elif note.child_id:
                    child = db.query(Child).filter(Child.id == note.child_id).first()
                    patient_name = child.name if child else "Çocuk hasta"
                else:
                    patient_name = "Hasta"

                create_notification_if_not_exists(
                    db,
                    user_id,
                    "Yaklaşan hasta görüşmesi",
                    f"{patient_name} için {visit_date.strftime('%Y-%m-%d')} tarihinde görüşme bulunmaktadır.",
                )


@app.get("/smart-notifications")
def smart_notifications(user_id: int, db: Session = Depends(get_db)):
    generate_smart_notifications_for_user(user_id=user_id, db=db)
    return get_notifications(user_id=user_id, db=db)


# =========================================================
# Rozet / Günlük Seri
# =========================================================

@app.get("/adult-gamification-v2")
def adult_gamification_v2(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")

    if user.role != "adult":
        raise HTTPException(status_code=403, detail="Bu rozet sistemi sadece yetişkin kullanıcılar içindir.")

    logs = db.query(DailyLog).filter(DailyLog.user_id == user_id).order_by(DailyLog.created_at.desc()).all()

    if not logs:
        return {
            "total_logs": 0,
            "total_days": 0,
            "current_streak": 0,
            "badges": [],
            "message": "Henüz günlük kayıt yok. İlk kaydını girerek serini başlatabilirsin.",
        }

    log_dates_set = set()
    for log in logs:
        if log.created_at:
            log_dates_set.add(log.created_at.date())

    log_dates = sorted(list(log_dates_set), reverse=True)
    total_logs = len(logs)
    total_days = len(log_dates)
    current_streak = 0

    if log_dates:
        expected_date = log_dates[0]
        for log_date in log_dates:
            if log_date == expected_date:
                current_streak += 1
                expected_date = expected_date - timedelta(days=1)
            else:
                break

    badges = []

    if total_logs >= 1:
        badges.append({"title": "İlk Adım", "description": "İlk günlük kaydını oluşturdun.", "level": "bronze"})
    if current_streak >= 3:
        badges.append({"title": "3 Günlük Seri", "description": "3 gün üst üste günlük kayıt girdin.", "level": "silver"})
    if current_streak >= 7:
        badges.append({"title": "7 Günlük Seri", "description": "7 gün üst üste takip alışkanlığı oluşturdun.", "level": "gold"})
    if total_logs >= 10:
        badges.append({"title": "Düzenli Takip", "description": "Toplam 10 günlük kayıt girdin.", "level": "gold"})

    today = date.today()

    if log_dates and log_dates[0] == today:
        if current_streak == 1:
            message = "Bugünkü kaydını girdin. Serin başladı!"
        elif current_streak < 3:
            message = f"Harika! {current_streak} günlük serin var. 3 güne ulaşırsan yeni rozet kazanırsın."
        elif current_streak < 7:
            message = f"Çok iyi! {current_streak} günlük serin var. 7 güne ulaşırsan altın rozet kazanırsın."
        else:
            message = f"Mükemmel! {current_streak} günlük güçlü bir takip serin var."
    else:
        message = f"Son kayıt serin {current_streak} gündü. Bugün kayıt girerek serini yeniden başlatabilirsin."

    return {
        "total_logs": total_logs,
        "total_days": total_days,
        "current_streak": current_streak,
        "badges": badges,
        "message": message,
    }
@app.post("/child-autism-test")
def create_child_autism_test(data: ChildAutismTestCreate, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == data.child_id).first()

    if not child:
        raise HTTPException(status_code=404, detail="Çocuk bulunamadı")

    scores = [
        data.A1_Score,
        data.A2_Score,
        data.A3_Score,
        data.A4_Score,
        data.A5_Score,
        data.A6_Score,
        data.A7_Score,
        data.A8_Score,
        data.A9_Score,
        data.A10_Score,
    ]

    total_score = sum(scores)

    if total_score <= 3:
        risk_level = "Düşük"
        result_text = "Çocuk için düşük düzeyde otizm belirtisi gözlemlenmiştir. Düzenli takip önerilir."
    elif total_score <= 6:
        risk_level = "Orta"
        result_text = "Çocuk için orta düzeyde belirti gözlemlenmiştir. Günlük takip ve uzman görüşü önerilir."
    else:
        risk_level = "Yüksek"
        result_text = "Çocuk için yüksek düzeyde belirti gözlemlenmiştir. Uzman değerlendirmesi önerilir."

    new_test = ChildAutismTest(
        child_id=data.child_id,
        A1_Score=data.A1_Score,
        A2_Score=data.A2_Score,
        A3_Score=data.A3_Score,
        A4_Score=data.A4_Score,
        A5_Score=data.A5_Score,
        A6_Score=data.A6_Score,
        A7_Score=data.A7_Score,
        A8_Score=data.A8_Score,
        A9_Score=data.A9_Score,
        A10_Score=data.A10_Score,
        age=data.age,
        total_score=total_score,
        risk_level=risk_level,
        result_text=result_text,
    )

    db.add(new_test)
    db.commit()
    db.refresh(new_test)

    create_notification(
        db=db,
        user_id=child.parent_id,
        title="Çocuk otizm testi kaydedildi",
        message=f"{child.name} için çocuk otizm ön tarama testi kaydedildi. Risk düzeyi: {risk_level}",
    )

    return {
        "message": "Çocuk otizm testi kaydedildi",
        "test_id": new_test.id,
        "child_id": data.child_id,
        "total_score": total_score,
        "risk_level": risk_level,
        "result_text": result_text,
    }


@app.get("/child-autism-tests")
def get_child_autism_tests(child_id: int, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == child_id).first()

    if not child:
        raise HTTPException(status_code=404, detail="Çocuk bulunamadı")

    records = (
        db.query(ChildAutismTest)
        .filter(ChildAutismTest.child_id == child_id)
        .order_by(ChildAutismTest.id.desc())
        .all()
    )

    return [
        {
            "id": record.id,
            "child_id": record.child_id,
            "A1_Score": record.A1_Score,
            "A2_Score": record.A2_Score,
            "A3_Score": record.A3_Score,
            "A4_Score": record.A4_Score,
            "A5_Score": record.A5_Score,
            "A6_Score": record.A6_Score,
            "A7_Score": record.A7_Score,
            "A8_Score": record.A8_Score,
            "A9_Score": record.A9_Score,
            "A10_Score": record.A10_Score,
            "age": record.age,
            "total_score": record.total_score,
            "risk_level": record.risk_level,
            "result_text": record.result_text,
            "created_at": str(record.created_at) if record.created_at else None,
        }
        for record in records
    ]