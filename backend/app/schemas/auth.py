"""Request/response schemas for the auth API."""
import uuid

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserRole

# Roles a person can self-assign at signup. Admin is deliberately excluded —
# allowing "role": "admin" on a public endpoint would be a privilege-escalation
# hole. Admin accounts are created only via app/seed_admin.py (see README).
SELF_REGISTERABLE_ROLES = {UserRole.PATIENT, UserRole.DOCTOR, UserRole.NURSE, UserRole.RECEPTION}


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=255)
    role: UserRole = UserRole.PATIENT

    @field_validator("role")
    @classmethod
    def reject_admin_self_registration(cls, value: UserRole) -> UserRole:
        if value not in SELF_REGISTERABLE_ROLES:
            raise ValueError(
                f"Cannot self-register with role '{value.value}'. "
                "Admin accounts are created via the seed_admin CLI script only."
            )
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}
