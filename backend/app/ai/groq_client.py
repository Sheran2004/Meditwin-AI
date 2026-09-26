"""
Thin wrapper around the Groq API for all LLM jobs in MediTwin AI:
  1. Report analysis: OCR'd text -> structured summary + abnormal values (EN/HI)
  2. Clinical decision support reasoning
  3. Drug interaction explanation
  4. Voice command intent parsing (Voice Assistant module)

Uses Groq's OpenAI-compatible chat completions API with JSON mode.
Kept as a single client module so there's one place that owns the API key,
model name, and JSON-output prompting discipline.
"""
import json

from groq import Groq

from app.core.config import settings

_MODEL_NAME = "openai/gpt-oss-120b"  # Groq's current developer-tier production model for
# complex structured-JSON tasks — llama-3.3-70b-versatile and llama-3.1-8b-instant were
# moved to Enterprise-only access on Groq (confirmed via console.groq.com/docs/models);
# this is Groq's own recommended replacement for that use case.


class GroqNotConfiguredError(Exception):
    pass


def _get_client() -> Groq:
    if not settings.GROQ_API_KEY:
        raise GroqNotConfiguredError(
            "GROQ_API_KEY is not set in the backend .env file. "
            "Get a key at https://console.groq.com/keys and add it before using AI features."
        )
    return Groq(api_key=settings.GROQ_API_KEY)


def _chat_json(system_prompt: str, user_prompt: str) -> dict:
    """Calls Groq with JSON mode and returns the parsed dict. Raises GroqNotConfiguredError if no key."""
    client = _get_client()
    completion = client.chat.completions.create(
        model=_MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
    )
    raw = completion.choices[0].message.content
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"_raw": raw}


def analyze_report_text(ocr_text: str, language: str = "en") -> dict:
    """
    Returns:
        {
          "summary": "plain-language summary",
          "abnormal_values": [{"name": str, "value": str, "normal_range": str, "explanation": str}],
          "language": "en" | "hi"
        }
    """
    lang_instruction = "Respond in Hindi (Devanagari script)." if language == "hi" else "Respond in English."

    system_prompt = f"""You are a medical report analysis assistant helping a patient understand their lab report.
{lang_instruction}
Return ONLY valid JSON matching exactly this shape:
{{
  "summary": "2-4 sentence plain-language summary of the overall report",
  "abnormal_values": [
    {{"name": "test name", "value": "the reported value", "normal_range": "normal range for this test", "explanation": "one sentence on what this means for the patient"}}
  ]
}}
If no values are abnormal, return an empty list for "abnormal_values". Do not invent values not present in the text."""

    user_prompt = f"REPORT TEXT:\n{ocr_text[:12000]}"

    parsed = _chat_json(system_prompt, user_prompt)
    if "_raw" in parsed:
        parsed = {"summary": parsed["_raw"], "abnormal_values": []}
    parsed["language"] = language
    return parsed


def clinical_decision_support(symptoms: str, patient_context: str = "") -> dict:
    """Used by the Clinical Decision Support module."""
    system_prompt = """You are assisting a doctor with a clinical decision support suggestion — NOT a diagnosis.
Return ONLY valid JSON matching exactly:
{
  "likely_conditions": [{"condition": "name", "confidence_pct": 0-100}],
  "recommended_tests": ["test1", "test2"],
  "red_flags": ["warning sign that needs immediate attention, if any"],
  "disclaimer": "This is an AI-generated suggestion for a licensed clinician's review, not a diagnosis."
}"""
    user_prompt = f"SYMPTOMS: {symptoms}" + (f"\nPATIENT CONTEXT: {patient_context}" if patient_context else "")

    parsed = _chat_json(system_prompt, user_prompt)
    if "_raw" in parsed:
        return {"likely_conditions": [], "recommended_tests": [], "red_flags": [], "disclaimer": parsed["_raw"]}
    return parsed


def drug_interaction_explanation(drug_names: list[str], rule_based_findings: dict) -> dict:
    """Takes the rule-based lookup result and asks the model to explain findings + suggest alternatives."""
    system_prompt = """You are a clinical pharmacology assistant. Return ONLY valid JSON matching exactly:
{
  "plain_language_summary": "2-3 sentence summary of the overall risk for a doctor to skim quickly",
  "alternative_suggestions": [{"replace": "drug name", "with": "safer alternative", "reason": "why"}],
  "disclaimer": "This is an AI-generated aid for a licensed clinician's review, not a substitute for a full drug interaction database."
}
If rule_based_findings shows no interactions, alternative_suggestions can be an empty list."""
    user_prompt = f"Medicine list: {', '.join(drug_names)}\nRule-based check found: {json.dumps(rule_based_findings)}"

    parsed = _chat_json(system_prompt, user_prompt)
    if "_raw" in parsed:
        return {"plain_language_summary": parsed["_raw"], "alternative_suggestions": [], "disclaimer": ""}
    return parsed


def parse_voice_command(transcript: str, known_patient_names: list[str]) -> dict:
    """
    Used by the Voice Assistant module. Maps a doctor's spoken command to a structured
    intent the frontend can act on (navigate to a patient, filter critical patients, etc.)
    """
    system_prompt = f"""You convert a doctor's spoken command into a structured action for a hospital dashboard.
Known patient names in this system: {', '.join(known_patient_names) if known_patient_names else '(none loaded)'}.

Return ONLY valid JSON matching exactly:
{{
  "intent": "show_patient" | "show_critical_patients" | "open_mri" | "compare_yesterday" | "generate_summary" | "unknown",
  "patient_name": "matched patient name if intent is show_patient, else null",
  "confirmation_text": "short spoken-style confirmation of what you understood"
}}"""
    parsed = _chat_json(system_prompt, f"COMMAND: {transcript}")
    if "_raw" in parsed:
        return {"intent": "unknown", "patient_name": None, "confirmation_text": "Sorry, I didn't understand that."}
    return parsed
