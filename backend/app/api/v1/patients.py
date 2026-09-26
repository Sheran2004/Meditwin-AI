"""Patient CRUD routes. RBAC: patients see only themselves; doctors/admins see all."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.patient import (
    MedicalHistoryCreate,
    MedicalHistoryResponse,
    PatientCreate,
    PatientResponse,
    PatientUpdate,
)
from app.services import patient_service
from app.services.patient_service import PatientAccessError, PatientNotFoundError

router = APIRouter(prefix="/patients", tags=["patients"])


def _to_response(patient, user) -> PatientResponse:
    return PatientResponse(
        id=patient.id,
        user_id=patient.user_id,
        full_name=user.full_name,
        email=user.email,
        date_of_birth=patient.date_of_birth,
        gender=patient.gender,
        blood_group=patient.blood_group,
        height_cm=float(patient.height_cm) if patient.height_cm is not None else None,
        weight_kg=float(patient.weight_kg) if patient.weight_kg is not None else None,
        assigned_doctor_id=patient.assigned_doctor_id,
        emergency_contact_name=patient.emergency_contact_name,
        emergency_contact_phone=patient.emergency_contact_phone,
        created_at=patient.created_at,
    )


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_my_patient_profile(
    payload: PatientCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PatientResponse:
    """A logged-in patient creates their own digital twin profile (one-time setup)."""
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only patient accounts can create a patient profile")
    patient = await patient_service.create_patient_profile(db, current_user, payload.model_dump())
    return _to_response(patient, current_user)


@router.get("", response_model=list[PatientResponse])
async def list_patients(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[PatientResponse]:
    rows = await patient_service.list_patients_for_user(db, current_user)
    return [_to_response(p, u) for p, u in rows]


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PatientResponse:
    try:
        patient, user = await patient_service.get_patient_with_user(db, patient_id)
        patient_service.assert_can_access_patient(current_user, patient)
    except PatientNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))
    except PatientAccessError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(e))
    return _to_response(patient, user)


@router.patch("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: uuid.UUID,
    payload: PatientUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PatientResponse:
    try:
        patient = await patient_service.get_patient_or_raise(db, patient_id)
        patient_service.assert_can_access_patient(current_user, patient)
    except PatientNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))
    except PatientAccessError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(e))

    updated = await patient_service.update_patient(db, patient, payload.model_dump(exclude_unset=True), current_user)
    _, user = await patient_service.get_patient_with_user(db, updated.id)
    return _to_response(updated, user)


@router.post("/{patient_id}/history", response_model=MedicalHistoryResponse, status_code=status.HTTP_201_CREATED)
async def add_history(
    patient_id: uuid.UUID,
    payload: MedicalHistoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MedicalHistoryResponse:
    """Doctors, nurses, and admins can add medical history entries — not reception or patients."""
    if current_user.role in (UserRole.PATIENT, UserRole.RECEPTION):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only clinical staff can add medical history entries")
    try:
        await patient_service.get_patient_or_raise(db, patient_id)
    except PatientNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))

    entry = await patient_service.add_medical_history(db, patient_id, payload.model_dump(), current_user)
    return MedicalHistoryResponse.model_validate(entry)


@router.get("/{patient_id}/history", response_model=list[MedicalHistoryResponse])
async def get_history(
    patient_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[MedicalHistoryResponse]:
    try:
        patient = await patient_service.get_patient_or_raise(db, patient_id)
        patient_service.assert_can_access_patient(current_user, patient)
    except PatientNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))
    except PatientAccessError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(e))

    entries = await patient_service.list_medical_history(db, patient_id)
    return [MedicalHistoryResponse.model_validate(e) for e in entries]
