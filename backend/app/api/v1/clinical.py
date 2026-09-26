"""Clinical Decision Support and Drug Interaction Checker routes. Doctor/admin only — these are clinician tools."""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.groq_client import GroqNotConfiguredError
from app.core.deps import require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.clinical import (
    ClinicalDecisionRequest,
    ClinicalDecisionResponse,
    DrugInteractionRequest,
    DrugInteractionResponse,
)
from app.services import clinical_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/clinical", tags=["clinical"])


@router.post("/decision-support", response_model=ClinicalDecisionResponse)
async def decision_support(
    payload: ClinicalDecisionRequest,
    current_user: User = Depends(require_roles(UserRole.DOCTOR, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> ClinicalDecisionResponse:
    try:
        result = await clinical_service.run_clinical_decision_support(
            db, None, payload.symptoms, payload.patient_context, current_user
        )
    except GroqNotConfiguredError as e:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(e))
    except Exception as e:
        logger.exception("Clinical decision support failed")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Decision support failed: {e}")
    return ClinicalDecisionResponse(**result)


@router.post("/drug-interactions", response_model=DrugInteractionResponse)
async def drug_interactions(
    payload: DrugInteractionRequest,
    current_user: User = Depends(require_roles(UserRole.DOCTOR, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> DrugInteractionResponse:
    try:
        result = await clinical_service.run_drug_interaction_check(db, None, payload.medicines, current_user)
    except GroqNotConfiguredError as e:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(e))
    except Exception as e:
        logger.exception("Drug interaction check failed")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Drug interaction check failed: {e}")
    return DrugInteractionResponse(
        interactions=result["interactions"],
        pregnancy_risk_drugs=result["pregnancy_risk_drugs"],
        kidney_risk_drugs=result["kidney_risk_drugs"],
        liver_risk_drugs=result["liver_risk_drugs"],
        plain_language_summary=result["plain_language_summary"],
        alternative_suggestions=[{"replace": s["replace"], "with": s["with"], "reason": s["reason"]} for s in result["alternative_suggestions"]],
        disclaimer=result["disclaimer"],
    )
