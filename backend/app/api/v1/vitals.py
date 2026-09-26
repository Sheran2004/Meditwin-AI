"""Vitals REST routes — manual entry + timeline. Live streaming is in app/ws/vitals_ws.py."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.vitals import AlertResponse, VitalsCreate, VitalsResponse
from app.services import alert_service, patient_service, vitals_service
from app.services.patient_service import PatientAccessError, PatientNotFoundError

router = APIRouter(prefix="/patients/{patient_id}/vitals", tags=["vitals"])


async def _check_access(db: AsyncSession, patient_id: uuid.UUID, current_user: User):
    try:
        patient = await patient_service.get_patient_or_raise(db, patient_id)
        patient_service.assert_can_access_patient(current_user, patient)
    except PatientNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))
    except PatientAccessError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(e))


@router.post("", response_model=VitalsResponse, status_code=status.HTTP_201_CREATED)
async def record_vitals(
    patient_id: uuid.UUID,
    payload: VitalsCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> VitalsResponse:
    await _check_access(db, patient_id, current_user)
    vitals, breaches = await vitals_service.record_vitals(db, patient_id, payload.model_dump(exclude_unset=True))
    # Critical breaches trigger a Twilio SMS to the patient's emergency contact
    # (falls back to a logged-only alert if Twilio/contact isn't configured —
    # see alert_service.raise_alerts_if_critical for the failure-safe design).
    await alert_service.raise_alerts_if_critical(db, patient_id, vitals, breaches)
    return VitalsResponse.model_validate(vitals)


@router.get("", response_model=list[VitalsResponse])
async def get_timeline(
    patient_id: uuid.UUID,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[VitalsResponse]:
    await _check_access(db, patient_id, current_user)
    entries = await vitals_service.get_vitals_timeline(db, patient_id, limit)
    return [VitalsResponse.model_validate(e) for e in entries]


@router.get("/alerts", response_model=list[AlertResponse])
async def get_alerts(
    patient_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[AlertResponse]:
    await _check_access(db, patient_id, current_user)
    alerts = await alert_service.list_alerts(db, patient_id)
    return [AlertResponse.model_validate(a) for a in alerts]
