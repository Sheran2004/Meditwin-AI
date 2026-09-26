"""
Auth service layer — keeps business logic out of the API route handlers
(clean architecture: routes stay thin, services own the logic, models own the data).
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.audit_log import AuditLog
from app.models.user import User, UserRole


class AuthError(Exception):
    """Raised for any auth failure — the API layer maps this to HTTP 401/409."""


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def register_user(db: AsyncSession, email: str, password: str, full_name: str, role: UserRole) -> User:
    existing = await get_user_by_email(db, email)
    if existing is not None:
        raise AuthError("An account with this email already exists")

    user = User(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        role=role,
    )
    db.add(user)
    await db.flush()

    db.add(AuditLog(user_id=user.id, action="user.register", resource="users", resource_id=str(user.id)))
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    user = await get_user_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        raise AuthError("Invalid email or password")
    if not user.is_active:
        raise AuthError("This account has been deactivated")

    db.add(AuditLog(user_id=user.id, action="user.login", resource="users", resource_id=str(user.id)))
    await db.commit()
    return user
