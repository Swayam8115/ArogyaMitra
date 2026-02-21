import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    base_url=os.getenv("GOOGLE_BASE_URL"),
)

MODEL_NAME = os.getenv("MODEL_NAME")

class LLMConclusion(BaseModel):
    diagnosis_summary: str
    confidence_interpretation: str
    severity_assessment: str
    key_contributing_factors: str
    recommended_next_steps: str
    referral_recommendation: str
    

def generate_llm_prompt(ml_result, graph_result):
    return (
        f"ML Analysis:\n"
        f"Disease: {ml_result['disease']}\n"
        f"Confidence: {ml_result['confidence']}\n"
        f"Precautions: {', '.join(ml_result['precautions'])}\n\n"
        f"Graph Analysis:\n"
        f"Insights: {graph_result['insights']}\n"
        f"Recommendations: {', '.join(graph_result['recommendations'])}\n"
    )

