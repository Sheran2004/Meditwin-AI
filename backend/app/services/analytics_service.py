"""
Analytics service — every number here is a real aggregate query against
the actual database. No hardcoded/mock stats: with an empty database this
correctly returns zeros, and grows accurately as real data is added.
"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.models.patient import Patient
from app.models.report import Report
from app.models.risk_score import RiskScore
from app.models.user import User, UserRole
from app.models.vitals import Vitals


async def get_hospital_analytics(db: AsyncSession) -> dict:
    total_patients = (await db.execute(select(func.count(Patient.id)).where(Patient.deleted_at.is_(None)))).scalar_one()
    total_doctors = (await db.execute(select(func.count(User.id)).where(User.role == UserRole.DOCTOR))).scalar_one()
    total_vitals_recorded = (await db.execute(select(func.count(Vitals.id)))).scalar_one()
    total_reports_analyzed = (await db.execute(select(func.count(Report.id)).where(Report.deleted_at.is_(None)))).scalar_one()
    total_alerts = (await db.execute(select(func.count(Alert.id)))).scalar_one()
    sms_alerts = (await db.execute(select(func.count(Alert.id)).where(Alert.sent_via == "sms"))).scalar_one()

    avg_risk_by_type = await db.execute(
        select(RiskScore.risk_type, func.avg(RiskScore.score_pct), func.count(RiskScore.id))
        .group_by(RiskScore.risk_type)
    )
    risk_breakdown = [
        {"risk_type": row[0].value, "avg_score_pct": round(float(row[1]), 1), "assessment_count": row[2]}
        for row in avg_risk_by_type.all()
    ]

    high_risk_count = (
        await db.execute(select(func.count(func.distinct(RiskScore.patient_id))).where(RiskScore.score_pct >= 70))
    ).scalar_one()

    most_common_alert_vital = await db.execute(
        select(Alert.trigger_vital, func.count(Alert.id)).group_by(Alert.trigger_vital).order_by(func.count(Alert.id).desc()).limit(5)
    )
    alert_breakdown = [{"vital": row[0], "count": row[1]} for row in most_common_alert_vital.all()]

    return {
        "total_patients": total_patients,
        "total_doctors": total_doctors,
        "total_vitals_recorded": total_vitals_recorded,
        "total_reports_analyzed": total_reports_analyzed,
        "total_alerts": total_alerts,
        "sms_alerts_sent": sms_alerts,
        "high_risk_patient_count": high_risk_count,
        "risk_breakdown": risk_breakdown,
        "alert_breakdown": alert_breakdown,
    }
