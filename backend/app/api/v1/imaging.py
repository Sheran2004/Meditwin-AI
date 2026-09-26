"""Medical imaging route — chest X-ray classification with Grad-CAM. See imaging_predictor.py's module docstring for the data-sufficiency caveat that every response carries."""
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.imaging_predictor import predict_pneumonia
from app.core.deps import require_roles
from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.user import User, UserRole
from app.services import patient_service
from app.services.patient_service import PatientNotFoundError

router = APIRouter(prefix="/patients/{patient_id}/imaging", tags=["imaging"])

MAX_FILE_SIZE_MB = 10


class ImagingResult(BaseModel):
    prediction: str
    confidence_pct: float
    heatmap: list[list[float]]
    clinically_meaningful: bool
    model_trained_on_n_images: int
    model_cv_accuracy: float
    model_cv_accuracy_std: float
    warning: str | None

    # Silences Pydantic's "model_*" protected-namespace warning — these
    # fields describe the ML model's stats, not pydantic model config.
    model_config = {"protected_namespaces": ()}


@router.post("/chest-xray", response_model=ImagingResult)
async def classify_chest_xray(
    patient_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles(UserRole.DOCTOR, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> ImagingResult:
    try:
        await patient_service.get_patient_or_raise(db, patient_id)
    except PatientNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))

    if file.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only JPEG/PNG images are supported")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"File exceeds {MAX_FILE_SIZE_MB}MB limit")

    result = predict_pneumonia(file_bytes)

    db.add(AuditLog(user_id=current_user.id, action="imaging.classify_chest_xray", resource="patients", resource_id=str(patient_id)))
    await db.commit()

    return ImagingResult(**result)
