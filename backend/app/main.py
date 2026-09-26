"""
MediTwin AI backend entrypoint.
Run locally with: uvicorn app.main:app --reload
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.ws.vitals_ws import router as vitals_ws_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)
app.include_router(vitals_ws_router)

# Serves uploaded report PDFs locally (Week 3 scope — swap for S3/Cloud
# storage + signed URLs before production, per the architecture doc).
_storage_dir = Path(__file__).parent / "storage"
_storage_dir.mkdir(exist_ok=True)
app.mount("/storage", StaticFiles(directory=str(_storage_dir)), name="storage")


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Used by Render/Docker health checks and the CI pipeline."""
    return {"status": "ok", "service": settings.PROJECT_NAME}
