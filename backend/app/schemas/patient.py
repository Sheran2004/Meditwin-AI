"""Request/response schemas for the patients API."""
import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class PatientCreate(BaseModel):
    date_of_birth: date | None = None
    gender: str | None = Field(default=None, max_length=20)
    blood_group: str | None = Field(default=None, max_length=5)
    height_cm: float | None = None
    weight_kg: float | None = None
    assigned_doctor_id: uuid.UUID | None = None
    emergency_contact_name: str | None = Field(default=None, max_length=255)
    emergency_contact_phone: str | None = Field(default=None, max_length=20, description="E.164 format, e.g. +919876543210")


class PatientUpdate(BaseModel):
    date_of_birth: date | None = None
    gender: str | None = None
    blood_group: str | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    assigned_doctor_id: uuid.UUID | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None


class PatientResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    full_name: str
    email: str
    date_of_birth: date | None
    gender: str | None
    blood_group: str | None
    height_cm: float | None
    weight_kg: float | None
    assigned_doctor_id: uuid.UUID | None
    emergency_contact_name: str | None
    emergency_contact_phone: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class MedicalHistoryCreate(BaseModel):
    condition: str = Field(min_length=1, max_length=255)
    diagnosed_at: date | None = None
    notes: str | None = None


class MedicalHistoryResponse(BaseModel):
    id: uuid.UUID
    condition: str
    diagnosed_at: date | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
