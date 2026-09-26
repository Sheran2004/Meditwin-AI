"""add nurse and reception roles

Revision ID: 0003
Revises: 0002
Create Date: 2026-08-05
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Postgres requires enum values to be added outside a transaction block in
    # older versions; ALTER TYPE ... ADD VALUE IF NOT EXISTS is safe on modern
    # Postgres (12+) run via autocommit, which Alembic handles per-migration.
    op.execute("ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'nurse'")
    op.execute("ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'reception'")


def downgrade() -> None:
    # Postgres does not support removing enum values directly. A downgrade
    # would require recreating the type; intentionally left as a no-op since
    # this is additive and safe to leave in place.
    pass
