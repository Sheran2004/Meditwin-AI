"""Aggregates every v1 sub-router. Add new module routers here as they're built."""
from fastapi import APIRouter

from app.api.v1.analytics import router as analytics_router
from app.api.v1.auth import router as auth_router
from app.api.v1.clinical import router as clinical_router
from app.api.v1.imaging import router as imaging_router
from app.api.v1.patients import router as patients_router
from app.api.v1.reports import router as reports_router
from app.api.v1.risk import router as risk_router
from app.api.v1.vitals import router as vitals_router
from app.api.v1.voice import router as voice_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(patients_router)
api_router.include_router(vitals_router)
api_router.include_router(risk_router)
api_router.include_router(reports_router)
api_router.include_router(clinical_router)
api_router.include_router(voice_router)
api_router.include_router(analytics_router)
api_router.include_router(imaging_router)
