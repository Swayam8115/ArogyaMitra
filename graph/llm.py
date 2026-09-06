import os
import json
import re
from pathlib import Path
from google import genai
from dotenv import load_dotenv
from pydantic import BaseModel

# Load .env from same directory as this file, regardless of CWD
load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-3.6-flash")

# Native Google GenAI client
client = genai.Client(api_key=GEMINI_API_KEY)


# ============================================================
# RESPONSE SCHEMA
# ============================================================

class LLMConclusion(BaseModel):
    diagnosis_summary: str
    confidence_interpretation: str
    severity_score: int
    severity_assessment: str
    key_contributing_factors: str
    recommended_next_steps: str
    referral_recommendation: str
    escalate_to_doctor: bool
    recommended_precautions: str


# ============================================================
# LLM CALL
# ============================================================

def call_llm(prompt: str) -> LLMConclusion:

    few_shot_example = {
        "diagnosis_summary": "The patient exhibits classic signs of Jaundice, supported by a 42.5% confidence score from the ML model.",
        "confidence_interpretation": "Moderate confidence. While Jaundice is the leading prediction, other related conditions should be excluded.",
        "severity_score": 4,
        "severity_assessment": "Moderate severity. Requires clinical monitoring, fluid replacement, and liver function tests.",
        "key_contributing_factors": "High bilirubin levels, physical symptoms (Jaundice), and patient history.",
        "recommended_next_steps": "Blood count, liver function tests, and ultrasound of the abdomen.",
        "referral_recommendation": "Gastroenterologist for specialized review.",
        "escalate_to_doctor": True,
        "recommended_precautions": "Stay hydrated, rest adequately, avoid alcohol, and follow medical advice closely."
    }

    full_prompt = (
        "You are a clinical decision-support assistant.\n"
        "Assess clinical severity on a 1-7 scale (1 = Low/Mild, 4 = Moderate, 7 = Severe/Critical) based on symptoms and diagnosis.\n"
        "You MUST return all JSON fields and ONLY valid JSON.\n"
        "Do NOT include any conversational text, headers, or markdown code blocks.\n"
        "Your response must start with '{' and end with '}'.\n\n"
        "Strict Schema:\n"
        "{\n"
        '  "diagnosis_summary": "string",\n'
        '  "confidence_interpretation": "string",\n'
        '  "severity_score": integer (1-7),\n'
        '  "severity_assessment": "string",\n'
        '  "key_contributing_factors": "string",\n'
        '  "recommended_next_steps": "string",\n'
        '  "referral_recommendation": "string",\n'
        '  "escalate_to_doctor": boolean,\n'
        '  "recommended_precautions": "string"\n'
        "}\n\n"
        f"Example Correct Output:\n{json.dumps(few_shot_example, indent=2)}\n\n"
        "Important: Return the raw JSON string starting with { and ending with }.\n\n"
        f"Now analyze this data and return only JSON matching the schema:\n\n{prompt}"
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=full_prompt,
    )

    response_content = response.text.strip()

    # Robustly extract JSON even if the model wraps it in markdown
    try:
        match = re.search(r"(\{.*\})", response_content, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            raise ValueError("Gemini did not return a JSON block.")

        llm_conclusion = LLMConclusion.model_validate_json(json_str)
        return llm_conclusion

    except Exception as e:
        raise ValueError(
            f"LLM Response Error: {e}. Raw content: {response_content}"
        )