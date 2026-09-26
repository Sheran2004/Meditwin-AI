"""Service layer for Clinical Decision Support and Drug Interaction Checker."""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai import drug_interactions
from app.ai.groq_client import clinical_decision_support, drug_interaction_explanation
from app.models.audit_log import AuditLog
from app.models.user import User


async def run_clinical_decision_support(
    db: AsyncSession, patient_id: uuid.UUID | None, symptoms: str, patient_context: str, acting_user: User
) -> dict:
    result = clinical_decision_support(symptoms, patient_context)
    db.add(AuditLog(
        user_id=acting_user.id, action="clinical.decision_support",
        resource="patients", resource_id=str(patient_id) if patient_id else "n/a",
    ))
    await db.commit()
    return result


async def run_drug_interaction_check(
    db: AsyncSession, patient_id: uuid.UUID | None, medicines: list[str], acting_user: User
) -> dict:
    rule_based = drug_interactions.check_interactions(medicines)
    ai_explanation = drug_interaction_explanation(medicines, rule_based)

    db.add(AuditLog(
        user_id=acting_user.id, action="clinical.drug_interaction_check",
        resource="patients", resource_id=str(patient_id) if patient_id else "n/a",
    ))
    await db.commit()

    return {
        **rule_based,
        "plain_language_summary": ai_explanation.get("plain_language_summary", ""),
        "alternative_suggestions": ai_explanation.get("alternative_suggestions", []),
        "disclaimer": ai_explanation.get("disclaimer", "This is an AI-generated aid for a licensed clinician's review."),
    }
