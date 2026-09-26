"""Schemas for Clinical Decision Support and Drug Interaction Checker (Week 4 modules)."""
from pydantic import BaseModel, Field


class ClinicalDecisionRequest(BaseModel):
    symptoms: str = Field(min_length=3, max_length=2000)
    patient_context: str = Field(default="", max_length=1000, description="Optional: age, known conditions, etc.")


class LikelyCondition(BaseModel):
    condition: str
    confidence_pct: float


class ClinicalDecisionResponse(BaseModel):
    likely_conditions: list[LikelyCondition]
    recommended_tests: list[str]
    red_flags: list[str]
    disclaimer: str


class DrugInteractionRequest(BaseModel):
    medicines: list[str] = Field(min_length=1, max_length=15)


class InteractionFinding(BaseModel):
    drug_a: str
    drug_b: str
    severity: str
    note: str


class AlternativeSuggestion(BaseModel):
    replace: str
    with_: str = Field(alias="with")
    reason: str

    model_config = {"populate_by_name": True}


class DrugInteractionResponse(BaseModel):
    interactions: list[InteractionFinding]
    pregnancy_risk_drugs: list[str]
    kidney_risk_drugs: list[str]
    liver_risk_drugs: list[str]
    plain_language_summary: str
    alternative_suggestions: list[AlternativeSuggestion]
    disclaimer: str
