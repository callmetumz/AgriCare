from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Animal, AuditLog, IllnessReport, OutbreakAlert, QuarantineEvent, VaccinationRecord
from .schemas import (
    AnimalCreate,
    AnimalOut,
    IllnessCreate,
    IllnessOut,
    QuarantineChange,
    QuarantineEventOut,
    VaccinationCreate,
    VaccinationOut,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AgriCare Prototype API", version="0.5.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND), name="static")

ROLE_ALIASES = {
    "care_staff": "Care Staff",
    "farmer": "Farmer/Owner",
    "manager": "Manager",
    "veterinarian": "Veterinarian",
    "administrator": "Administrator",
    "auditor": "Auditor",
}

from .rules import classify_severity, calculate_next_due, transition_allowed


def get_role(x_role: Annotated[str | None, Header()] = None) -> str:
    role = (x_role or "care_staff").strip().lower()
    if role not in ROLE_ALIASES:
        raise HTTPException(400, "Unknown demo role")
    return role


def audit(db: Session, action: str, entity_type: str, entity_id: int | None, role: str, details: str = ""):
    db.add(AuditLog(action=action, entity_type=entity_type, entity_id=entity_id, role=role, details=details))


def update_outbreak_alert(db: Session, animal: Animal, body_system: str):
    cutoff = datetime.utcnow() - timedelta(hours=72)
    count_stmt = (
        select(func.count(func.distinct(IllnessReport.animal_id)))
        .join(Animal, IllnessReport.animal_id == Animal.id)
        .where(
            Animal.enclosure == animal.enclosure,
            IllnessReport.body_system == body_system,
            IllnessReport.created_at >= cutoff,
        )
    )
    count = int(db.scalar(count_stmt) or 0)
    if count >= 3:
        exists_stmt = select(OutbreakAlert).where(
            OutbreakAlert.enclosure == animal.enclosure,
            OutbreakAlert.body_system == body_system,
            OutbreakAlert.status == "Open",
        )
        if not db.scalar(exists_stmt):
            db.add(OutbreakAlert(enclosure=animal.enclosure, body_system=body_system, animal_count=count))


@app.get("/")
def index():
    return FileResponse(FRONTEND / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "prototype": "AgriCare Step 5", "version": app.version}


@app.get("/api/animals", response_model=list[AnimalOut])
def list_animals(db: Session = Depends(get_db)):
    return list(db.scalars(select(Animal).where(Animal.archived.is_(False)).order_by(Animal.tag_id)))


@app.post("/api/animals", response_model=AnimalOut, status_code=201)
def create_animal(payload: AnimalCreate, db: Session = Depends(get_db), role: str = Depends(get_role)):
    if role not in {"care_staff", "farmer", "manager"}:
        raise HTTPException(403, "This demo role cannot create animal profiles")
    if db.scalar(select(Animal).where(Animal.tag_id == payload.tag_id)):
        raise HTTPException(409, "Tag ID already exists")
    animal = Animal(**payload.model_dump())
    db.add(animal)
    db.flush()
    audit(db, "CREATE_ANIMAL", "Animal", animal.id, role, f"tag={animal.tag_id}")
    db.commit()
    db.refresh(animal)
    return animal


@app.post("/api/animals/{animal_id}/illness", response_model=IllnessOut, status_code=201)
def report_illness(animal_id: int, payload: IllnessCreate, db: Session = Depends(get_db), role: str = Depends(get_role)):
    if role not in {"care_staff", "farmer", "veterinarian"}:
        raise HTTPException(403, "This demo role cannot record illness reports")
    animal = db.get(Animal, animal_id)
    if not animal or animal.archived:
        raise HTTPException(404, "Animal not found")
    severity = classify_severity(payload.symptoms, payload.fever)
    report = IllnessReport(
        animal_id=animal.id,
        symptoms=", ".join(payload.symptoms),
        body_system=payload.body_system,
        notes=payload.notes,
        severity=severity,
        created_by_role=role,
    )
    db.add(report)
    if severity in {"Moderate", "Urgent"} and animal.quarantine_state == "Healthy":
        previous = animal.quarantine_state
        animal.quarantine_state = "Suspect"
        db.add(QuarantineEvent(
            animal_id=animal.id,
            from_state=previous,
            to_state="Suspect",
            reason=f"Automatic suspect flag after {severity.lower()} illness report",
            changed_by_role="system",
        ))
    db.flush()
    update_outbreak_alert(db, animal, payload.body_system)
    audit(db, "REPORT_ILLNESS", "IllnessReport", report.id, role, f"severity={severity}; animal={animal.tag_id}")
    db.commit()
    db.refresh(report)
    return report


@app.post("/api/animals/{animal_id}/vaccinations", response_model=VaccinationOut, status_code=201)
def record_vaccination(animal_id: int, payload: VaccinationCreate, db: Session = Depends(get_db), role: str = Depends(get_role)):
    if role != "veterinarian":
        raise HTTPException(403, "Only the Veterinarian role can record vaccinations")
    animal = db.get(Animal, animal_id)
    if not animal:
        raise HTTPException(404, "Animal not found")
    next_due = calculate_next_due(payload.date_administered, payload.booster_interval_days)
    record = VaccinationRecord(animal_id=animal.id, next_due_date=next_due, **payload.model_dump())
    db.add(record)
    db.flush()
    audit(db, "RECORD_VACCINATION", "VaccinationRecord", record.id, role, f"animal={animal.tag_id}; due={next_due}")
    db.commit()
    db.refresh(record)
    return record


@app.post("/api/animals/{animal_id}/quarantine", response_model=QuarantineEventOut, status_code=201)
def change_quarantine(animal_id: int, payload: QuarantineChange, db: Session = Depends(get_db), role: str = Depends(get_role)):
    if role != "veterinarian":
        raise HTTPException(403, "Only the Veterinarian role can change quarantine state")
    animal = db.get(Animal, animal_id)
    if not animal:
        raise HTTPException(404, "Animal not found")
    current = animal.quarantine_state
    target = payload.to_state
    if not transition_allowed(current, target):
        raise HTTPException(400, f"Invalid transition: {current} -> {target}")
    event = QuarantineEvent(
        animal_id=animal.id,
        from_state=current,
        to_state=target,
        reason=payload.reason,
        changed_by_role=role,
    )
    animal.quarantine_state = target
    db.add(event)
    db.flush()
    audit(db, "CHANGE_QUARANTINE", "QuarantineEvent", event.id, role, f"{current}->{target}; animal={animal.tag_id}")
    db.commit()
    db.refresh(event)
    return event


@app.get("/api/animals/{animal_id}/history")
def animal_history(animal_id: int, db: Session = Depends(get_db)):
    animal = db.get(Animal, animal_id)
    if not animal:
        raise HTTPException(404, "Animal not found")
    illnesses = list(db.scalars(select(IllnessReport).where(IllnessReport.animal_id == animal_id).order_by(IllnessReport.created_at.desc())))
    vaccinations = list(db.scalars(select(VaccinationRecord).where(VaccinationRecord.animal_id == animal_id).order_by(VaccinationRecord.date_administered.desc())))
    quarantine = list(db.scalars(select(QuarantineEvent).where(QuarantineEvent.animal_id == animal_id).order_by(QuarantineEvent.changed_at.desc())))
    return {
        "animal": AnimalOut.model_validate(animal),
        "illnesses": [IllnessOut.model_validate(x) for x in illnesses],
        "vaccinations": [VaccinationOut.model_validate(x) for x in vaccinations],
        "quarantine_events": [QuarantineEventOut.model_validate(x) for x in quarantine],
    }


@app.get("/api/dashboard")
def dashboard(db: Session = Depends(get_db)):
    today = date.today()
    total_animals = int(db.scalar(select(func.count()).select_from(Animal).where(Animal.archived.is_(False))) or 0)
    quarantined = int(db.scalar(select(func.count()).select_from(Animal).where(Animal.quarantine_state.in_(["Suspect", "Isolated", "Monitored"]))) or 0)
    urgent_cases = int(db.scalar(select(func.count()).select_from(IllnessReport).where(IllnessReport.severity == "Urgent")) or 0)
    overdue_vaccinations = int(db.scalar(select(func.count()).select_from(VaccinationRecord).where(VaccinationRecord.next_due_date < today)) or 0)
    open_outbreaks = int(db.scalar(select(func.count()).select_from(OutbreakAlert).where(OutbreakAlert.status == "Open")) or 0)
    return {
        "total_animals": total_animals,
        "quarantined": quarantined,
        "urgent_cases": urgent_cases,
        "overdue_vaccinations": overdue_vaccinations,
        "open_outbreaks": open_outbreaks,
    }


@app.get("/api/outbreak-alerts")
def outbreak_alerts(db: Session = Depends(get_db)):
    alerts = list(db.scalars(select(OutbreakAlert).order_by(OutbreakAlert.created_at.desc())))
    return [
        {
            "id": a.id,
            "enclosure": a.enclosure,
            "body_system": a.body_system,
            "animal_count": a.animal_count,
            "status": a.status,
            "created_at": a.created_at,
        }
        for a in alerts
    ]


@app.get("/api/audit")
def audit_log(db: Session = Depends(get_db), role: str = Depends(get_role)):
    if role not in {"auditor", "administrator", "manager"}:
        raise HTTPException(403, "Audit log is restricted")
    items = list(db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(100)))
    return [
        {
            "id": x.id,
            "action": x.action,
            "entity_type": x.entity_type,
            "entity_id": x.entity_id,
            "role": x.role,
            "details": x.details,
            "created_at": x.created_at,
        }
        for x in items
    ]
