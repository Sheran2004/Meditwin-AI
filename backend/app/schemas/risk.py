"""
Request/response schemas for the risk prediction API.
Note: risk assessment takes its own clinical input form (not the continuous
vitals table) because the trained models need specific clinical fields
(cholesterol, exercise test results, etc.) that aren't part of routine
vitals monitoring — this mirrors how a real risk calculator works.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class HeartRiskInput(BaseModel):
    age: int = Field(ge=1, le=120)
    sex: int = Field(ge=0, le=1, description="1 = male, 0 = female")
    cp: int = Field(ge=0, le=3, description="chest pain type (0-3)")
    trestbps: int = Field(ge=50, le=260, description="resting blood pressure (mmHg)")
    chol: int = Field(ge=50, le=700, description="serum cholesterol (mg/dl)")
    fbs: int = Field(ge=0, le=1, description="fasting blood sugar > 120 mg/dl (1=true)")
    restecg: int = Field(ge=0, le=2, description="resting ECG results (0-2)")
    thalach: int = Field(ge=50, le=250, description="max heart rate achieved")
    exang: int = Field(ge=0, le=1, description="exercise-induced angina (1=yes)")
    oldpeak: float = Field(ge=0, le=10, description="ST depression induced by exercise")
    slope: int = Field(ge=0, le=2, description="slope of peak exercise ST segment")
    ca: int = Field(ge=0, le=4, description="number of major vessels colored by fluoroscopy")
    thal: int = Field(ge=0, le=3, description="thalassemia (0-3)")


class DiabetesRiskInput(BaseModel):
    Pregnancies: int = Field(ge=0, le=20)
    Glucose: int = Field(ge=0, le=300)
    BloodPressure: int = Field(ge=0, le=200)
    SkinThickness: int = Field(ge=0, le=100)
    Insulin: int = Field(ge=0, le=900)
    BMI: float = Field(ge=0, le=80)
    DiabetesPedigreeFunction: float = Field(ge=0, le=3)
    Age: int = Field(ge=1, le=120)


class RiskAssessmentResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    risk_type: str
    score_pct: float
    confidence: float
    reasoning: str
    recommendation: str
    model_accuracy: float
    computed_at: datetime

    model_config = {"from_attributes": True, "protected_namespaces": ()}
