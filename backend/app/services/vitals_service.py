"""
Vitals service layer.
record_vitals() also runs a critical-threshold check so the Emergency
Alert module (Week 4) can hang off the same write path without the API
route needing to know about it.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vitals import Vitals

# Simple critical thresholds — used by the emergency alert module.
# Kept here (not hardcoded in routes) so they're the single source of truth.
CRITICAL_THRESHOLDS = {
    "spo2": {"below": 90},
    "heart_rate": {"below": 40, "above": 150},
    "bp_systolic": {"above": 180},
    "temperature": {"above": 40.0},
}


def check_critical_vitals(vitals: Vitals) -> list[dict]:
    """Returns a list of breached thresholds, e.g. [{"vital": "spo2", "value": 85, "rule": "below 90"}]."""
    breaches = []
    for field, rules in CRITICAL_THRESHOLDS.items():
        value = getattr(vitals, field, None)
        if value is None:
            continue
        if "below" in rules and value < rules["below"]:
            breaches.append({"vital": field, "value": value, "rule": f"below {rules['below']}"})
        if "above" in rules and value > rules["above"]:
            breaches.append({"vital": field, "value": value, "rule": f"above {rules['above']}"})
    return breaches


async def record_vitals(db: AsyncSession, patient_id: uuid.UUID, data: dict) -> tuple[Vitals, list[dict]]:
    vitals = Vitals(patient_id=patient_id, **data)
    db.add(vitals)
    await db.commit()
    await db.refresh(vitals)
    breaches = check_critical_vitals(vitals)
    return vitals, breaches


async def get_vitals_timeline(db: AsyncSession, patient_id: uuid.UUID, limit: int = 50) -> list[Vitals]:
    result = await db.execute(
        select(Vitals).where(Vitals.patient_id == patient_id).order_by(Vitals.recorded_at.desc()).limit(limit)
    )
    return list(result.scalars().all())[::-1]  # oldest -> newest, ready for charting
