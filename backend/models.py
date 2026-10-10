from datetime import datetime
from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from .database import Base


class Animal(Base):
    __tablename__ = "animals"

    id = Column(Integer, primary_key=True)
    tag_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(80), nullable=True)
    species = Column(String(80), nullable=False)
    breed = Column(String(80), nullable=True)
    sex = Column(String(20), nullable=True)
    age_years = Column(Float, nullable=True)
    enclosure = Column(String(100), nullable=False)
    weight_kg = Column(Float, nullable=True)
    temperature_c = Column(Float, nullable=True)
    quarantine_state = Column(String(20), default="Healthy", nullable=False)
    archived = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    illnesses = relationship("IllnessReport", back_populates="animal", cascade="all, delete-orphan")
    vaccinations = relationship("VaccinationRecord", back_populates="animal", cascade="all, delete-orphan")
    quarantine_events = relationship("QuarantineEvent", back_populates="animal", cascade="all, delete-orphan")


class IllnessReport(Base):
    __tablename__ = "illness_reports"

    id = Column(Integer, primary_key=True)
    animal_id = Column(Integer, ForeignKey("animals.id"), nullable=False, index=True)
    symptoms = Column(Text, nullable=False)
    body_system = Column(String(80), default="General", nullable=False)
    notes = Column(Text, nullable=True)
    onset = Column(DateTime, default=datetime.utcnow, nullable=False)
    severity = Column(String(20), nullable=False)
    created_by_role = Column(String(40), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    animal = relationship("Animal", back_populates="illnesses")


class VaccinationRecord(Base):
    __tablename__ = "vaccination_records"

    id = Column(Integer, primary_key=True)
    animal_id = Column(Integer, ForeignKey("animals.id"), nullable=False, index=True)
    vaccine_name = Column(String(120), nullable=False)
    batch_number = Column(String(100), nullable=True)
    dosage = Column(String(80), nullable=True)
    date_administered = Column(Date, nullable=False)
    booster_interval_days = Column(Integer, nullable=False)
    next_due_date = Column(Date, nullable=False)
    veterinarian = Column(String(120), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    animal = relationship("Animal", back_populates="vaccinations")


class QuarantineEvent(Base):
    __tablename__ = "quarantine_events"

    id = Column(Integer, primary_key=True)
    animal_id = Column(Integer, ForeignKey("animals.id"), nullable=False, index=True)
    from_state = Column(String(20), nullable=False)
    to_state = Column(String(20), nullable=False)
    reason = Column(Text, nullable=False)
    changed_by_role = Column(String(40), nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    animal = relationship("Animal", back_populates="quarantine_events")


class OutbreakAlert(Base):
    __tablename__ = "outbreak_alerts"

    id = Column(Integer, primary_key=True)
    enclosure = Column(String(100), nullable=False)
    body_system = Column(String(80), nullable=False)
    animal_count = Column(Integer, nullable=False)
    status = Column(String(20), default="Open", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    action = Column(String(120), nullable=False)
    entity_type = Column(String(80), nullable=False)
    entity_id = Column(Integer, nullable=True)
    role = Column(String(40), nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
