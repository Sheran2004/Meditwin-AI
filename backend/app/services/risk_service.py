"""Risk service — calls the AI predictor, persists the result, returns it."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.risk_predictor import predict_diabetes_risk, predict_heart_risk
from app.models.audit_log import AuditLog
from app.models.risk_score import RiskScore, RiskType
from app.models.user import User


async def assess_heart_risk(db: AsyncSession, patient_id: uuid.UUID, features: dict, acting_user: User) -> dict:
    result = predict_heart_risk(features)
    score = RiskScore(
        patient_id=patient_id,
        risk_type=RiskType.HEART_ATTACK,
        score_pct=result["risk_pct"],
        confidence=result["confidence"],
        reasoning=f"{result['reasoning']} {result['recommendation']}",  # combined for storage (single text column)
    )
    db.add(score)
    await db.flush()
    db.add(AuditLog(user_id=acting_user.id, action="risk.assess_heart", resource="risk_scores", resource_id=str(score.id)))
    await db.commit()
    await db.refresh(score)
    return {**result, "id": score.id, "patient_id": score.patient_id, "risk_type": score.risk_type.value, "computed_at": score.computed_at}


async def assess_diabetes_risk(db: AsyncSession, patient_id: uuid.UUID, features: dict, acting_user: User) -> dict:
    result = predict_diabetes_risk(features)
    score = RiskScore(
        patient_id=patient_id,
        risk_type=RiskType.DIABETES,
        score_pct=result["risk_pct"],
        confidence=result["confidence"],
        reasoning=f"{result['reasoning']} {result['recommendation']}",  # combined for storage (single text column)
    )
    db.add(score)
    await db.flush()
    db.add(AuditLog(user_id=acting_user.id, action="risk.assess_diabetes", resource="risk_scores", resource_id=str(score.id)))
    await db.commit()
    await db.refresh(score)
    return {**result, "id": score.id, "patient_id": score.patient_id, "risk_type": score.risk_type.value, "computed_at": score.computed_at}


async def list_risk_scores(db: AsyncSession, patient_id: uuid.UUID) -> list[RiskScore]:
    result = await db.execute(
        select(RiskScore).where(RiskScore.patient_id == patient_id).order_by(RiskScore.computed_at.desc())
    )
    return list(result.scalars().all())
