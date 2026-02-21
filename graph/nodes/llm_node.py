from llm import call_llm
import json

def llm_node(state):
    xai_data = state["xai_output"]

    prompt = f"""
    Below is structured output from a trained Explainable AI model.

    Rules:
    - Do NOT modify predicted disease.
    - Do NOT introduce new diagnoses.
    - Use only the provided data.

    XAI Output:
    {json.dumps(xai_data, indent=2)}
    """

    structured_summary = call_llm(prompt)

    return {
        "llm_summary": structured_summary
    }