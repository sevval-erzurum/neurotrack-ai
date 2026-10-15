from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from app.database import Base
from sqlalchemy import DateTime
from datetime import datetime

# -----------------
# USER TABLOSU
# -----------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)


# -----------------
# PREDICTION TABLOSU
# -----------------
class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    result = Column(Integer)
    age = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class DailyLog(Base):
    __tablename__ = "daily_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    mood = Column(String, nullable=False)
    sleep_hours = Column(Integer)
    social_interaction = Column(Integer)
    note = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class DoctorPatient(Base):
    __tablename__ = "doctor_patient"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"))
    patient_id = Column(Integer, ForeignKey("users.id"))

class ClinicalFollowUp(Base):
    __tablename__ = "clinical_followups"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    meltdown = Column(String)
    sensory_sensitivity = Column(Integer)
    eye_contact = Column(Integer)
    communication_willingness = Column(Integer)
    routine_reaction = Column(Integer)
    eating_pattern = Column(String)
    medication_therapy = Column(String)
    school_work_performance = Column(Integer)
    self_harm_risk = Column(String)
    note = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

class Child(Base):
    __tablename__ = "children"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("users.id"))

    name = Column(String)
    age = Column(Integer)
    gender = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

class ChildDailyLog(Base):
    __tablename__ = "child_daily_logs"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"))
    mood = Column(String, nullable=False)
    sleep_hours = Column(Integer)
    social_interaction = Column(Integer)
    note = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class DoctorChild(Base):
    __tablename__ = "doctor_child"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"))
    child_id = Column(Integer, ForeignKey("children.id"))

class ChildClinicalFollowUp(Base):
    __tablename__ = "child_clinical_followups"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"))

    meltdown = Column(String)
    sensory_sensitivity = Column(Integer)
    eye_contact = Column(Integer)
    communication_willingness = Column(Integer)
    routine_reaction = Column(Integer)
    eating_pattern = Column(String)
    medication_therapy = Column(String)
    note = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

class DoctorNote(Base):
    __tablename__ = "doctor_notes"

    id = Column(Integer, primary_key=True, index=True)

    doctor_id = Column(Integer, ForeignKey("users.id"))
    child_id = Column(Integer, ForeignKey("children.id"), nullable=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    note = Column(String)
    recommendation = Column(String)
    next_visit_date = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    content = Column(Text, nullable=False)

    is_read = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
class MessageRequest(Base):
    __tablename__ = "message_requests"

    id = Column(Integer, primary_key=True, index=True)

    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    status = Column(String, default="pending")  # pending / accepted / rejected

    created_at = Column(DateTime, default=datetime.utcnow)
class ChildAutismTest(Base):
    __tablename__ = "child_autism_tests"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"))

    A1_Score = Column(Integer)
    A2_Score = Column(Integer)
    A3_Score = Column(Integer)
    A4_Score = Column(Integer)
    A5_Score = Column(Integer)
    A6_Score = Column(Integer)
    A7_Score = Column(Integer)
    A8_Score = Column(Integer)
    A9_Score = Column(Integer)
    A10_Score = Column(Integer)

    age = Column(Integer)
    total_score = Column(Integer)
    risk_level = Column(String)
    result_text = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)