"""
Report model — an uploaded PDF/lab report plus the AI pipeline's output.
ai_summary and abnormal_values are JSONB: this is what replaces a
document store (MongoDB) for unstructured AI-generated content, per
the architecture doc's stack-trimming decision.
"""
import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base_class import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    file_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    ocr_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_summary: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    abnormal_values: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en")  # "en" or "hi"
    uploaded_at: Mapped[datetime] = mapped_column(server_default=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True)  # soft delete
