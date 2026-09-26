"""Hospital analytics route — admin/doctor only. All figures are live DB aggregates."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


class RiskBreakdownItem(BaseModel):
    risk_type: str
    avg_score_pct: float
    assessment_count: int


class AlertBreakdownItem(BaseModel):
    vital: str
    count: int


class HospitalAnalyticsResponse(BaseModel):
    total_patients: int
    total_doctors: int
    total_vitals_recorded: int
    total_reports_analyzed: int
    total_alerts: int
    sms_alerts_sent: int
    high_risk_patient_count: int
    risk_breakdown: list[RiskBreakdownItem]
    alert_breakdown: list[AlertBreakdownItem]


@router.get("/hospital", response_model=HospitalAnalyticsResponse)
async def hospital_analytics(
    current_user: User = Depends(require_roles(UserRole.DOCTOR, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> HospitalAnalyticsResponse:
    data = await analytics_service.get_hospital_analytics(db)
    return HospitalAnalyticsResponse(**data)
