"""
Vitals model — one row per measurement snapshot.
Fed by manual entry (Week 2) and later a simulated live stream over WebSocket.
Indexed on (patient_id, recorded_at) since the timeline view always queries
"latest N vitals for this patient".
"""
import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Index, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base_class import Base


class Vitals(Base):
    __tablename__ = "vitals"
    __table_args__ = (Index("ix_vitals_patient_recorded", "patient_id", "recorded_at"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)          # bpm
    bp_systolic: Mapped[int | None] = mapped_column(Integer, nullable=True)         # mmHg
    bp_diastolic: Mapped[int | None] = mapped_column(Integer, nullable=True)        # mmHg
    spo2: Mapped[int | None] = mapped_column(Integer, nullable=True)                # %
    temperature: Mapped[float | None] = mapped_column(Numeric(4, 1), nullable=True)  # Celsius
    blood_sugar: Mapped[int | None] = mapped_column(Integer, nullable=True)         # mg/dL
    respiration: Mapped[int | None] = mapped_column(Integer, nullable=True)         # breaths/min
    recorded_at: Mapped[datetime] = mapped_column(server_default=func.now())
