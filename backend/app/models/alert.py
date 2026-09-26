"""Alert model — emergency notifications (Week 4 module), logged for audit/demo."""
import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base_class import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    trigger_vital: Mapped[str] = mapped_column(String(50), nullable=False)   # e.g. "spo2"
    threshold: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    sent_via: Mapped[str] = mapped_column(String(20), nullable=False)  # "sms" | "email" | "push"
    sent_at: Mapped[datetime] = mapped_column(server_default=func.now())
