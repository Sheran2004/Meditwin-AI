"""
Aggregates every model so Base.metadata is fully populated.
Import Base FROM HERE only in places that need the full metadata
(Alembic's env.py). Models themselves import Base from base_class.py
directly to avoid a circular import.
"""
from app.db.base_class import Base

# Import every model module here so Base.metadata is fully populated
# before Alembic (or anything else) inspects it.
from app.models.user import User  # noqa: E402, F401
from app.models.patient import Patient  # noqa: E402, F401
from app.models.vitals import Vitals  # noqa: E402, F401
from app.models.medical_history import MedicalHistory  # noqa: E402, F401
from app.models.report import Report  # noqa: E402, F401
from app.models.risk_score import RiskScore  # noqa: E402, F401
from app.models.alert import Alert  # noqa: E402, F401
from app.models.audit_log import AuditLog  # noqa: E402, F401
