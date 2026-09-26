"""initial schema - users, patients, vitals, medical_history, reports, risk_scores, alerts, audit_logs

Revision ID: 0001
Revises:
Create Date: 2026-08-04
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    user_role = postgresql.ENUM(
        "admin", "doctor", "patient", name="user_role", create_type=False
    )
    risk_type = postgresql.ENUM(
        "heart_attack", "stroke", "diabetes", "icu_admission", "readmission",
        name="risk_type", create_type=False
    )
    # Create enums only once (safe if already exist)
    op.execute("DO $$ BEGIN CREATE TYPE user_role AS ENUM ('admin', 'doctor', 'patient'); EXCEPTION WHEN duplicate_object THEN null; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE risk_type AS ENUM ('heart_attack', 'stroke', 'diabetes', 'icu_admission', 'readmission'); EXCEPTION WHEN duplicate_object THEN null; END $$;")

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "patients",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("gender", sa.String(20), nullable=True),
        sa.Column("blood_group", sa.String(5), nullable=True),
        sa.Column("height_cm", sa.Numeric(5, 1), nullable=True),
        sa.Column("weight_kg", sa.Numeric(5, 1), nullable=True),
        sa.Column("assigned_doctor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "vitals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("heart_rate", sa.Integer(), nullable=True),
        sa.Column("bp_systolic", sa.Integer(), nullable=True),
        sa.Column("bp_diastolic", sa.Integer(), nullable=True),
        sa.Column("spo2", sa.Integer(), nullable=True),
        sa.Column("temperature", sa.Numeric(4, 1), nullable=True),
        sa.Column("blood_sugar", sa.Integer(), nullable=True),
        sa.Column("respiration", sa.Integer(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_vitals_patient_recorded", "vitals", ["patient_id", "recorded_at"])

    op.create_table(
        "medical_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("condition", sa.String(255), nullable=False),
        sa.Column("diagnosed_at", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("file_url", sa.String(1024), nullable=False),
        sa.Column("ocr_text", sa.Text(), nullable=True),
        sa.Column("ai_summary", postgresql.JSONB(), nullable=True),
        sa.Column("abnormal_values", postgresql.JSONB(), nullable=True),
        sa.Column("language", sa.String(10), nullable=False, server_default="en"),
        sa.Column("uploaded_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "risk_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("risk_type", risk_type, nullable=False),
        sa.Column("score_pct", sa.Numeric(5, 2), nullable=False),
        sa.Column("confidence", sa.Numeric(5, 2), nullable=False),
        sa.Column("reasoning", sa.Text(), nullable=True),
        sa.Column("computed_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("trigger_vital", sa.String(50), nullable=False),
        sa.Column("threshold", sa.Numeric(6, 2), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("sent_via", sa.String(20), nullable=False),
        sa.Column("sent_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource", sa.String(100), nullable=False),
        sa.Column("resource_id", sa.String(100), nullable=True),
        sa.Column("timestamp", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("alerts")
    op.drop_table("risk_scores")
    op.drop_table("reports")
    op.drop_table("medical_history")
    op.drop_table("vitals")
    op.drop_table("patients")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    postgresql.ENUM(name="risk_type").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="user_role").drop(op.get_bind(), checkfirst=True)
