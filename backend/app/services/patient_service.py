"""
Patient service layer.
Access rule: a patient can only ever see their own record; a doctor/admin
can see any patient. This rule lives here (not scattered across routes)
so it's enforced consistently everywhere patients are read.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.audit_log import AuditLog
from app.models.medical_history import MedicalHistory
from app.models.patient import Patient
from app.models.user import User, UserRole


class PatientAccessError(Exception):
    """Raised when a user tries to access a patient record they don't own."""


class PatientNotFoundError(Exception):
    pass


async def create_patient_profile(db: AsyncSession, user: User, data: dict) -> Patient:
    """Called once, right after a user registers with role=patient."""
    patient = Patient(user_id=user.id, **data)
    db.add(patient)
    await db.flush()
    db.add(AuditLog(user_id=user.id, action="patient.create", resource="patients", resource_id=str(patient.id)))
    await db.commit()
    await db.refresh(patient)
    return patient


async def get_patient_or_raise(db: AsyncSession, patient_id: uuid.UUID) -> Patient:
    result = await db.execute(select(Patient).where(Patient.id == patient_id, Patient.deleted_at.is_(None)))
    patient = result.scalar_one_or_none()
    if patient is None:
        raise PatientNotFoundError(f"No patient found with id {patient_id}")
    return patient


def assert_can_access_patient(current_user: User, patient: Patient) -> None:
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise PatientAccessError("You can only access your own patient record")


async def list_patients_for_user(db: AsyncSession, current_user: User) -> list[tuple[Patient, User]]:
    """Clinical/front-desk staff (doctor/nurse/reception/admin) see everyone; a patient sees only themselves."""
    query = select(Patient, User).join(User, Patient.user_id == User.id).where(Patient.deleted_at.is_(None))
    if current_user.role == UserRole.PATIENT:
        query = query.where(Patient.user_id == current_user.id)
    result = await db.execute(query)
    return list(result.all())


async def get_patient_with_user(db: AsyncSession, patient_id: uuid.UUID) -> tuple[Patient, User]:
    result = await db.execute(
        select(Patient, User).join(User, Patient.user_id == User.id).where(Patient.id == patient_id, Patient.deleted_at.is_(None))
    )
    row = result.first()
    if row is None:
        raise PatientNotFoundError(f"No patient found with id {patient_id}")
    return row


async def update_patient(db: AsyncSession, patient: Patient, data: dict, acting_user: User) -> Patient:
    for key, value in data.items():
        if value is not None:
            setattr(patient, key, value)
    db.add(AuditLog(user_id=acting_user.id, action="patient.update", resource="patients", resource_id=str(patient.id)))
    await db.commit()
    await db.refresh(patient)
    return patient


async def add_medical_history(db: AsyncSession, patient_id: uuid.UUID, data: dict, acting_user: User) -> MedicalHistory:
    entry = MedicalHistory(patient_id=patient_id, **data)
    db.add(entry)
    await db.flush()
    db.add(AuditLog(user_id=acting_user.id, action="medical_history.create", resource="medical_history", resource_id=str(entry.id)))
    await db.commit()
    await db.refresh(entry)
    return entry


async def list_medical_history(db: AsyncSession, patient_id: uuid.UUID) -> list[MedicalHistory]:
    result = await db.execute(
        select(MedicalHistory).where(MedicalHistory.patient_id == patient_id).order_by(MedicalHistory.diagnosed_at.desc())
    )
    return list(result.scalars().all())
