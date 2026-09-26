"""Request/response schemas for the vitals API."""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class VitalsCreate(BaseModel):
    heart_rate: int | None = Field(default=None, ge=20, le=250)
    bp_systolic: int | None = Field(default=None, ge=50, le=260)
    bp_diastolic: int | None = Field(default=None, ge=30, le=180)
    spo2: int | None = Field(default=None, ge=0, le=100)
    temperature: float | None = Field(default=None, ge=25, le=45)
    blood_sugar: int | None = Field(default=None, ge=0, le=700)
    respiration: int | None = Field(default=None, ge=0, le=80)


class VitalsResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    heart_rate: int | None
    bp_systolic: int | None
    bp_diastolic: int | None
    spo2: int | None
    temperature: float | None
    blood_sugar: int | None
    respiration: int | None
    recorded_at: datetime

    model_config = {"from_attributes": True}


class AlertResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    trigger_vital: str
    threshold: float
    message: str
    sent_via: str
    sent_at: datetime

    model_config = {"from_attributes": True}
