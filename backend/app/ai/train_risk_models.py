"""
Trains the two P0 risk models on real public clinical datasets:
  - Heart disease risk: UCI Cleveland Heart Disease dataset (303 patients)
  - Diabetes risk: Pima Indians Diabetes dataset (768 patients)

These are small, well-known teaching datasets — good enough to produce a
genuinely-trained, genuinely-predictive model for a hackathon demo, but
NOT large enough for clinical deployment. That distinction belongs in the
demo script: "trained on the UCI Cleveland dataset" is accurate and
defensible; "clinically validated" would not be.

Run manually whenever you want to retrain: python -m app.ai.train_risk_models
Produces, per model, two files in app/ai/models/:
  - <name>_model.json  — the XGBoost booster itself, in XGBoost's native
    format (model.save_model()) rather than pickled. This is the
    XGBoost-recommended approach: it's stable across library versions and
    doesn't trigger the "loading a pickled model" compatibility warning.
  - <name>_model_meta.json — plain JSON: {"features": [...], "accuracy": float}
"""
import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

DATA_DIR = Path(__file__).parent / "data"
MODELS_DIR = Path(__file__).parent / "models"
MODELS_DIR.mkdir(exist_ok=True)

HEART_FEATURES = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal"]
DIABETES_FEATURES = ["Pregnancies", "Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"]


def _train_and_save(csv_path: Path, features: list[str], target: str, name: str, flip_target: bool = False) -> None:
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=features + [target])

    X = df[features]
    y = df[target]
    if flip_target:
        # This particular UCI heart-disease mirror encodes target=1 as "no disease"
        # and target=0 as "disease present" (verified against clinical markers:
        # the target=0 group has higher cholesterol/BP/oldpeak and lower max heart
        # rate — the classic at-risk profile). Flip so 1 always means "at risk"
        # to match risk_pct semantics used everywhere else in this API.
        y = 1 - y
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = XGBClassifier(
        n_estimators=150,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        eval_metric="logloss",
        random_state=42,
    )
    model.fit(X_train, y_train)

    accuracy = accuracy_score(y_test, model.predict(X_test))
    print(f"[{name}] test accuracy: {accuracy:.3f} (n_train={len(X_train)}, n_test={len(X_test)})")

    model.save_model(MODELS_DIR / f"{name}_model.json")
    with open(MODELS_DIR / f"{name}_model_meta.json", "w") as f:
        json.dump({"features": features, "accuracy": round(float(accuracy), 3)}, f)
    print(f"[{name}] saved -> {MODELS_DIR / f'{name}_model.json'}")


def train_all() -> None:
    _train_and_save(DATA_DIR / "heart.csv", HEART_FEATURES, "target", "heart", flip_target=True)
    _train_and_save(DATA_DIR / "diabetes.csv", DIABETES_FEATURES, "Outcome", "diabetes")


if __name__ == "__main__":
    train_all()
