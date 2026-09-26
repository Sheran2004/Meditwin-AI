"""
Report service: saves the uploaded file to local disk (Week 3 scope —
swap for S3/Cloud storage before production, per the architecture doc),
runs OCR, calls Groq for the structured summary, and persists everything.
"""
import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.groq_client import analyze_report_text
from app.ai.ocr import extract_text_from_pdf
from app.models.audit_log import AuditLog
from app.models.report import Report
from app.models.user import User

STORAGE_DIR = Path(__file__).parent.parent / "storage" / "reports"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


async def upload_and_analyze_report(
    db: AsyncSession, patient_id: uuid.UUID, filename: str, file_bytes: bytes, language: str, acting_user: User
) -> Report:
    report_id = uuid.uuid4()
    safe_name = f"{report_id}_{filename.replace('/', '_')}"
    file_path = STORAGE_DIR / safe_name
    file_path.write_bytes(file_bytes)

    ocr_text = extract_text_from_pdf(file_bytes)
    analysis = analyze_report_text(ocr_text, language=language) if ocr_text else {
        "summary": "No readable text could be extracted from this file.",
        "abnormal_values": [],
        "language": language,
    }

    report = Report(
        id=report_id,
        patient_id=patient_id,
        file_url=f"/storage/reports/{safe_name}",
        ocr_text=ocr_text,
        ai_summary={"summary": analysis.get("summary", "")},
        abnormal_values={"items": analysis.get("abnormal_values", [])},
        language=language,
    )
    db.add(report)
    await db.flush()
    db.add(AuditLog(user_id=acting_user.id, action="report.upload_analyze", resource="reports", resource_id=str(report.id)))
    await db.commit()
    await db.refresh(report)
    return report


async def list_reports(db: AsyncSession, patient_id: uuid.UUID) -> list[Report]:
    result = await db.execute(
        select(Report).where(Report.patient_id == patient_id, Report.deleted_at.is_(None)).order_by(Report.uploaded_at.desc())
    )
    return list(result.scalars().all())
