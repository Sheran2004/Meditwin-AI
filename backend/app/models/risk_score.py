"""Risk score model — output of the AI Risk Prediction module (Week 2)."""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Enum, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base_class import Base


class RiskType(str, enum.Enum):
    HEART_ATTACK = "heart_attack"
    STROKE = "stroke"
    DIABETES = "diabetes"
    ICU_ADMISSION = "icu_admission"
    READMISSION = "readmission"


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    risk_type: Mapped[RiskType] = mapped_column(Enum(RiskType, name="risk_type"), nullable=False)
    score_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    confidence: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    computed_at: Mapped[datetime] = mapped_column(server_default=func.now())
