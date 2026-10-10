from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class AnimalCreate(BaseModel):
    tag_id: str = Field(min_length=1, max_length=50)
    name: Optional[str] = None
    species: str
    breed: Optional[str] = None
    sex: Optional[str] = None
    age_years: Optional[float] = None
    enclosure: str
    weight_kg: Optional[float] = None
    temperature_c: Optional[float] = None


class AnimalOut(AnimalCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    quarantine_state: str
    archived: bool
    created_at: datetime


class IllnessCreate(BaseModel):
    symptoms: list[str] = Field(min_length=1)
    body_system: str = "General"
    notes: Optional[str] = None
    fever: bool = False


class IllnessOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    animal_id: int
    symptoms: str
    body_system: str
    notes: Optional[str]
    severity: str
    created_by_role: str
    created_at: datetime


class VaccinationCreate(BaseModel):
    vaccine_name: str
    batch_number: Optional[str] = None
    dosage: Optional[str] = None
    date_administered: date
    booster_interval_days: int = Field(gt=0, le=3650)
    veterinarian: str


class VaccinationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    animal_id: int
    vaccine_name: str
    batch_number: Optional[str]
    dosage: Optional[str]
    date_administered: date
    booster_interval_days: int
    next_due_date: date
    veterinarian: str


class QuarantineChange(BaseModel):
    to_state: str
    reason: str = Field(min_length=3)


class QuarantineEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    animal_id: int
    from_state: str
    to_state: str
    reason: str
    changed_by_role: str
    changed_at: datetime
