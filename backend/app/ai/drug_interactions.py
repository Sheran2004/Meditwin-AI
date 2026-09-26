"""
Rule-based drug interaction lookup.
This is a small, curated table of well-documented dangerous interactions —
not a substitute for a licensed drug interaction database (e.g. Micromedex,
Lexicomp) in production, but real, correct, and defensible for a hackathon
demo. Groq (Llama) is used on top of this to explain *why* in plain language and
to catch pairs not in the table (clearly labeled as AI-generated when it does).
"""

# Keys are lowercase generic drug names. Each entry lists (other_drug, severity, description).
KNOWN_INTERACTIONS: dict[str, list[dict]] = {
    "warfarin": [
        {"with": "aspirin", "severity": "high", "note": "Both increase bleeding risk; combination significantly raises risk of major hemorrhage."},
        {"with": "ibuprofen", "severity": "high", "note": "NSAIDs increase bleeding risk and can reduce warfarin's anticoagulant control."},
    ],
    "aspirin": [
        {"with": "warfarin", "severity": "high", "note": "Both increase bleeding risk; combination significantly raises risk of major hemorrhage."},
        {"with": "ibuprofen", "severity": "medium", "note": "Ibuprofen can reduce aspirin's cardioprotective antiplatelet effect if timed incorrectly."},
    ],
    "ibuprofen": [
        {"with": "warfarin", "severity": "high", "note": "NSAIDs increase bleeding risk and can reduce warfarin's anticoagulant control."},
        {"with": "aspirin", "severity": "medium", "note": "Ibuprofen can reduce aspirin's cardioprotective antiplatelet effect if timed incorrectly."},
        {"with": "lisinopril", "severity": "medium", "note": "NSAIDs can reduce the blood-pressure-lowering effect of ACE inhibitors and stress the kidneys."},
    ],
    "lisinopril": [
        {"with": "ibuprofen", "severity": "medium", "note": "NSAIDs can reduce the blood-pressure-lowering effect of ACE inhibitors and stress the kidneys."},
        {"with": "potassium", "severity": "high", "note": "ACE inhibitors + potassium supplements can cause dangerous hyperkalemia."},
        {"with": "spironolactone", "severity": "high", "note": "Both raise potassium — combination risks dangerous hyperkalemia."},
    ],
    "metformin": [
        {"with": "contrast dye", "severity": "high", "note": "Risk of lactic acidosis if renal function drops after iodinated contrast — usually held around imaging procedures."},
    ],
    "simvastatin": [
        {"with": "clarithromycin", "severity": "high", "note": "Strong CYP3A4 inhibition raises statin levels sharply, increasing risk of rhabdomyolysis."},
        {"with": "grapefruit", "severity": "medium", "note": "Grapefruit juice inhibits statin metabolism, raising blood levels and side-effect risk."},
    ],
    "sildenafil": [
        {"with": "nitroglycerin", "severity": "high", "note": "Combination can cause a severe, life-threatening drop in blood pressure."},
    ],
    "tramadol": [
        {"with": "sertraline", "severity": "high", "note": "Both raise serotonin — combination risks serotonin syndrome."},
        {"with": "fluoxetine", "severity": "high", "note": "Both raise serotonin — combination risks serotonin syndrome."},
    ],
}

# Pregnancy-risk and organ-risk flags (simplified, illustrative — real system would use a full formulary).
PREGNANCY_RISK_DRUGS = {"warfarin", "ibuprofen", "simvastatin", "lisinopril"}
KIDNEY_RISK_DRUGS = {"ibuprofen", "lisinopril", "metformin"}
LIVER_RISK_DRUGS = {"simvastatin", "acetaminophen", "paracetamol"}


def check_interactions(drug_names: list[str]) -> dict:
    normalized = [d.strip().lower() for d in drug_names if d.strip()]
    interactions_found = []
    seen_pairs = set()

    for drug in normalized:
        for interaction in KNOWN_INTERACTIONS.get(drug, []):
            other = interaction["with"]
            if other in normalized:
                pair_key = tuple(sorted([drug, other]))
                if pair_key not in seen_pairs:
                    seen_pairs.add(pair_key)
                    interactions_found.append({
                        "drug_a": drug, "drug_b": other,
                        "severity": interaction["severity"], "note": interaction["note"],
                    })

    return {
        "interactions": interactions_found,
        "pregnancy_risk_drugs": sorted(set(normalized) & PREGNANCY_RISK_DRUGS),
        "kidney_risk_drugs": sorted(set(normalized) & KIDNEY_RISK_DRUGS),
        "liver_risk_drugs": sorted(set(normalized) & LIVER_RISK_DRUGS),
    }
