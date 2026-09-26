"""Risk prediction routes — only doctors/admins can run an assessment; patients can view their own results."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.risk import DiabetesRiskInput, HeartRiskInput, RiskAssessmentResponse
from app.services import patient_service, risk_service
from app.services.patient_service import PatientAccessError, PatientNotFoundError

router = APIRouter(prefix="/patients/{patient_id}/risk", tags=["risk"])


@router.post("/heart-attack", response_model=RiskAssessmentResponse, status_code=status.HTTP_201_CREATED)
async def assess_heart_attack_risk(
    patient_id: uuid.UUID,
    payload: HeartRiskInput,
    current_user: User = Depends(require_roles(UserRole.DOCTOR, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> RiskAssessmentResponse:
    try:
        await patient_service.get_patient_or_raise(db, patient_id)
    except PatientNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))

    score = await risk_service.assess_heart_risk(db, patient_id, payload.model_dump(), current_user)
    return RiskAssessmentResponse(
        id=score["id"], patient_id=score["patient_id"], risk_type=score["risk_type"],
        score_pct=score["risk_pct"], confidence=score["confidence"],
        reasoning=score["reasoning"], recommendation=score["recommendation"],
        model_accuracy=score["model_accuracy"], computed_at=score["computed_at"],
    )


@router.post("/diabetes", response_model=RiskAssessmentResponse, status_code=status.HTTP_201_CREATED)
async def assess_diabetes_risk(
    patient_id: uuid.UUID,
    payload: DiabetesRiskInput,
    current_user: User = Depends(require_roles(UserRole.DOCTOR, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> RiskAssessmentResponse:
    try:
        await patient_service.get_patient_or_raise(db, patient_id)
    except PatientNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))

    score = await risk_service.assess_diabetes_risk(db, patient_id, payload.model_dump(), current_user)
    return RiskAssessmentResponse(
        id=score["id"], patient_id=score["patient_id"], risk_type=score["risk_type"],
        score_pct=score["risk_pct"], confidence=score["confidence"],
        reasoning=score["reasoning"], recommendation=score["recommendation"],
        model_accuracy=score["model_accuracy"], computed_at=score["computed_at"],
    )


@router.get("", response_model=list[RiskAssessmentResponse])
async def list_risk_history(
    patient_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[RiskAssessmentResponse]:
    try:
        patient = await patient_service.get_patient_or_raise(db, patient_id)
        patient_service.assert_can_access_patient(current_user, patient)
    except PatientNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))
    except PatientAccessError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(e))

    scores = await risk_service.list_risk_scores(db, patient_id)
    return [
        RiskAssessmentResponse(
            id=s.id, patient_id=s.patient_id, risk_type=s.risk_type.value,
            score_pct=float(s.score_pct), confidence=float(s.confidence),
            reasoning=s.reasoning, recommendation="", model_accuracy=0.0, computed_at=s.computed_at,
        )
        for s in scores
    ]
