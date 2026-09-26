"""
Voice Assistant route. The browser's native Web Speech API does the actual
speech-to-text (free, no external STT service needed); this endpoint takes
the resulting transcript and asks Groq to map it to a structured action
the frontend can execute (navigate to a patient, filter critical patients, etc).
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.ai.groq_client import GroqNotConfiguredError, parse_voice_command
from app.core.deps import require_roles
from app.models.user import User, UserRole
from app.schemas.voice import VoiceCommandRequest, VoiceCommandResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/command", response_model=VoiceCommandResponse)
async def voice_command(
    payload: VoiceCommandRequest,
    current_user: User = Depends(require_roles(UserRole.DOCTOR, UserRole.ADMIN)),
) -> VoiceCommandResponse:
    try:
        result = parse_voice_command(payload.transcript, payload.known_patient_names)
    except GroqNotConfiguredError as e:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(e))
    except Exception as e:
        logger.exception("Voice command parsing failed")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Voice command failed: {e}")
    return VoiceCommandResponse(**result)
