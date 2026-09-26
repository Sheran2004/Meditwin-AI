"""
Creates an admin account directly in the database.
Admin is intentionally NOT selectable on the public /register endpoint or
the register page dropdown — allowing self-registration as admin would be
a privilege-escalation hole in a real hospital system. This script is the
correct way to create the first admin account.

Usage:
    cd backend
    python -m app.seed_admin admin@meditwin.ai "Admin Name" yourpassword123
"""
import asyncio
import sys

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.user import User, UserRole
from app.services.auth_service import get_user_by_email


async def seed_admin(email: str, full_name: str, password: str) -> None:
    async with AsyncSessionLocal() as db:
        existing = await get_user_by_email(db, email)
        if existing is not None:
            print(f"A user with email {email} already exists (role: {existing.role.value}).")
            if existing.role != UserRole.ADMIN:
                existing.role = UserRole.ADMIN
                await db.commit()
                print("Promoted existing account to admin.")
            return

        admin = User(email=email, password_hash=hash_password(password), full_name=full_name, role=UserRole.ADMIN)
        db.add(admin)
        await db.commit()
        print(f"Admin account created: {email}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python -m app.seed_admin <email> <full_name> <password>")
        sys.exit(1)
    asyncio.run(seed_admin(sys.argv[1], sys.argv[2], sys.argv[3]))
