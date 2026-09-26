"""add emergency contact fields to patients

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-04
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("patients", sa.Column("emergency_contact_name", sa.String(255), nullable=True))
    op.add_column("patients", sa.Column("emergency_contact_phone", sa.String(20), nullable=True))


def downgrade() -> None:
    op.drop_column("patients", "emergency_contact_phone")
    op.drop_column("patients", "emergency_contact_name")
