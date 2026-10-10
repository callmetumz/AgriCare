from datetime import date, timedelta
from sqlalchemy import select
from .database import Base, SessionLocal, engine
from .models import Animal, AuditLog, IllnessReport, QuarantineEvent, VaccinationRecord

Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    if db.scalar(select(Animal).limit(1)):
        print("Database already contains data; seed skipped.")
    else:
        animals = [
            Animal(tag_id="RFID-001", name="Luna", species="Cattle", breed="Nguni", sex="Female", age_years=4, enclosure="North Paddock", weight_kg=410, temperature_c=38.5),
            Animal(tag_id="RFID-002", name="Milo", species="Goat", breed="Boer", sex="Male", age_years=2, enclosure="Goat Pen A", weight_kg=72, temperature_c=39.1, quarantine_state="Suspect"),
            Animal(tag_id="RFID-003", name="Nala", species="Cattle", breed="Bonsmara", sex="Female", age_years=3, enclosure="North Paddock", weight_kg=455, temperature_c=38.8, quarantine_state="Monitored"),
            Animal(tag_id="RFID-004", name="Kudu-17", species="Kudu", breed="Greater Kudu", sex="Female", age_years=5, enclosure="Sanctuary East", weight_kg=180, temperature_c=39.0),
        ]
        db.add_all(animals)
        db.flush()
        db.add(VaccinationRecord(
            animal_id=animals[0].id,
            vaccine_name="Clostridial 8-in-1",
            batch_number="C8-2608",
            dosage="2 ml",
            date_administered=date.today() - timedelta(days=380),
            booster_interval_days=365,
            next_due_date=date.today() - timedelta(days=15),
            veterinarian="Dr Mokoena",
        ))
        db.add(IllnessReport(
            animal_id=animals[2].id,
            symptoms="fever, loss of appetite",
            body_system="General",
            notes="Observed during morning round",
            severity="Moderate",
            created_by_role="care_staff",
        ))
        db.add(IllnessReport(
            animal_id=animals[1].id,
            symptoms="breathing difficulty",
            body_system="Respiratory",
            notes="Red-flag sign observed in Goat Pen A",
            severity="Urgent",
            created_by_role="care_staff",
        ))
        db.add(QuarantineEvent(
            animal_id=animals[1].id,
            from_state="Healthy",
            to_state="Suspect",
            reason="Urgent illness report",
            changed_by_role="system",
        ))
        db.add(QuarantineEvent(
            animal_id=animals[2].id,
            from_state="Isolated",
            to_state="Monitored",
            reason="Symptoms improving after treatment",
            changed_by_role="veterinarian",
        ))
        db.add(AuditLog(action="SEED_DEMO_DATA", entity_type="System", entity_id=None, role="system", details="Initial Step 5 prototype data"))
        db.commit()
        print("Seeded AgriCare prototype data.")
finally:
    db.close()
