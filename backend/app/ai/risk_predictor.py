"""
Loads the trained models once at import time and exposes
predict_heart_risk() / predict_diabetes_risk().

Models are loaded via XGBoost's native format (model.load_model()), not
pickle — see train_risk_models.py's module docstring for why.

Explainability approach: XGBoost's built-in feature_importances_ tells us
which features matter *in general*; we combine that with which of *this
patient's* values fall outside a normal clinical range to generate the
"reasoning" and "recommendation" text the architecture doc requires
(Risk %, Confidence, Reason, Recommendation) — this is a lightweight,
defensible substitute for full SHAP value computation, appropriate for
a hackathon timeline.
"""
import json
from pathlib import Path

from xgboost import XGBClassifier

MODELS_DIR = Path(__file__).parent / "models"

# (feature_key, "friendly label", normal_range) — used to build reasoning text.
HEART_NORMAL_RANGES = {
    "trestbps": ("resting blood pressure", 90, 130),
    "chol": ("cholesterol", 0, 200),
    "thalach": ("max heart rate achieved", 100, 190),  # inverse: LOWER than expected is a risk signal here
    "oldpeak": ("ST depression (exercise-induced)", 0, 1.0),
}
DIABETES_NORMAL_RANGES = {
    "Glucose": ("glucose level", 70, 140),
    "BMI": ("BMI", 18.5, 25),
    "BloodPressure": ("blood pressure", 60, 120),
    "Insulin": ("insulin level", 16, 166),
}


def _load(name: str) -> dict:
    model = XGBClassifier()
    model.load_model(MODELS_DIR / f"{name}_model.json")
    with open(MODELS_DIR / f"{name}_model_meta.json") as f:
        meta = json.load(f)
    return {"model": model, "features": meta["features"], "accuracy": meta["accuracy"]}


_heart_bundle = _load("heart")
_diabetes_bundle = _load("diabetes")


def _predict(bundle: dict, features: dict, normal_ranges: dict, risk_name: str) -> dict:
    model = bundle["model"]
    feature_order = bundle["features"]

    row = [[features[f] for f in feature_order]]
    proba = model.predict_proba(row)[0]
    risk_pct = round(float(proba[1]) * 100, 1)

    # Confidence = how far the model's probability sits from the 50/50 line —
    # a prediction of 92% or 8% is more confident than one sitting at 51%.
    confidence = round(float(abs(proba[1] - 0.5) * 2) * 100, 1)

    # Combine global feature importance with this patient's out-of-range values
    # to produce plain-language reasoning.
    importances = dict(zip(feature_order, model.feature_importances_))
    flagged = []
    for key, (label, lo, hi) in normal_ranges.items():
        value = features.get(key)
        if value is None:
            continue
        if value < lo or value > hi:
            flagged.append((label, value, lo, hi, importances.get(key, 0)))
    flagged.sort(key=lambda x: x[4], reverse=True)  # most important flags first

    if flagged:
        parts = [f"{label} of {value} is outside the normal range ({lo}-{hi})" for label, value, lo, hi, _ in flagged[:3]]
        reasoning = f"Elevated {risk_name.replace('_', ' ')} risk driven by: " + "; ".join(parts) + "."
    else:
        reasoning = f"No major out-of-range clinical values detected; {risk_name.replace('_', ' ')} risk is largely baseline for this patient's profile."

    if risk_pct >= 70:
        recommendation = "High risk — recommend urgent clinical review and confirmatory testing."
    elif risk_pct >= 40:
        recommendation = "Moderate risk — recommend follow-up testing and lifestyle counseling."
    else:
        recommendation = "Low risk — recommend routine monitoring at the next scheduled check-up."

    return {
        "risk_pct": risk_pct,
        "confidence": confidence,
        "reasoning": reasoning,
        "recommendation": recommendation,
        "model_accuracy": bundle["accuracy"],
    }


def predict_heart_risk(features: dict) -> dict:
    """features must contain: age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal"""
    return _predict(_heart_bundle, features, HEART_NORMAL_RANGES, "heart_attack")


def predict_diabetes_risk(features: dict) -> dict:
    """features must contain: Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age"""
    return _predict(_diabetes_bundle, features, DIABETES_NORMAL_RANGES, "diabetes")
