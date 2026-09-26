"""Request/response schemas for the medical report analyzer API."""
import uuid
from datetime import datetime

from pydantic import BaseModel


class AbnormalValue(BaseModel):
    name: str
    value: str
    normal_range: str
    explanation: str


class ReportResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    file_url: str
    ai_summary: dict | None
    abnormal_values: dict | None
    language: str
    uploaded_at: datetime

    model_config = {"from_attributes": True}
