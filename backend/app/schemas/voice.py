"""Schemas for the Voice Assistant module."""
from pydantic import BaseModel


class VoiceCommandRequest(BaseModel):
    transcript: str
    known_patient_names: list[str] = []


class VoiceCommandResponse(BaseModel):
    intent: str
    patient_name: str | None
    confirmation_text: str
