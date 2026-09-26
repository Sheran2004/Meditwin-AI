"""Report upload + AI analysis routes."""
import logging
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.groq_client import GroqNotConfiguredError
from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.report import ReportResponse
from app.services import patient_service, report_service
from app.services.patient_service import PatientAccessError, PatientNotFoundError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/patients/{patient_id}/reports", tags=["reports"])

MAX_FILE_SIZE_MB = 15


async def _check_access(db: AsyncSession, patient_id: uuid.UUID, current_user: User):
    try:
        patient = await patient_service.get_patient_or_raise(db, patient_id)
        patient_service.assert_can_access_patient(current_user, patient)
    except PatientNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))
    except PatientAccessError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(e))


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def upload_report(
    patient_id: uuid.UUID,
    file: UploadFile = File(...),
    language: str = Query(default="en", pattern="^(en|hi)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReportResponse:
    await _check_access(db, patient_id, current_user)

    if file.content_type != "application/pdf":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only PDF files are supported")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"File exceeds {MAX_FILE_SIZE_MB}MB limit")

    try:
        report = await report_service.upload_and_analyze_report(
            db, patient_id, file.filename, file_bytes, language, current_user
        )
    except GroqNotConfiguredError as e:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(e))
    except Exception as e:
        # Catch-all so the frontend always gets a real, specific error message
        # instead of a bare 500 with no body (which forces a generic guess in
        # the UI). Logged with the full traceback for local debugging.
        logger.exception("Report upload/analysis failed for patient %s", patient_id)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Report analysis failed: {e}")

    return ReportResponse.model_validate(report)


@router.get("", response_model=list[ReportResponse])
async def list_patient_reports(
    patient_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ReportResponse]:
    await _check_access(db, patient_id, current_user)
    reports = await report_service.list_reports(db, patient_id)
    return [ReportResponse.model_validate(r) for r in reports]
