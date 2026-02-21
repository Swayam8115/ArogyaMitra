from utils.pdf_generator import generate_pdf
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import joblib
import numpy as np
import io
import os

# Load Model Artifacts 
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'model')

# On HF Spaces the model/ folder won't exist so download from HF Hub
if not os.path.exists(os.path.join(MODEL_DIR, 'disease_model.pkl')):
    print("Downloading model from Hugging Face Hub...")
    from huggingface_hub import snapshot_download
    snapshot_download(
        repo_id="DashAyush/arogyamitra-model",
        repo_type="model",
        local_dir=MODEL_DIR
    )
    print("Download complete!")

model           = joblib.load(os.path.join(MODEL_DIR, 'disease_model.pkl'))
label_encoder   = joblib.load(os.path.join(MODEL_DIR, 'label_encoder.pkl'))
symptom_cols    = joblib.load(os.path.join(MODEL_DIR, 'symptom_columns.pkl'))
X_train         = joblib.load(os.path.join(MODEL_DIR, 'X_train.pkl'))
severity_map    = joblib.load(os.path.join(MODEL_DIR, 'severity_map.pkl'))
description_map = joblib.load(os.path.join(MODEL_DIR, 'description_map.pkl'))
precaution_map  = joblib.load(os.path.join(MODEL_DIR, 'precaution_map.pkl'))
disease_classes = list(label_encoder.classes_)

# Rebuild LIME explainer from saved training data (can't pickle lambda functions)
import lime.lime_tabular
lime_explainer = lime.lime_tabular.LimeTabularExplainer(
    training_data=X_train,
    feature_names=symptom_cols,
    class_names=disease_classes,
    mode='classification',
    random_state=42
)


app = FastAPI(title="ArogyaMitra ML API", version="1.0.0")

# Request Schema
class PredictRequest(BaseModel):
    symptoms: List[str]
    patientName: Optional[str] = "Patient"
    patientAge: Optional[int] = None
    patientGender: Optional[str] = None
    workerName: Optional[str] = "Healthcare Worker"
    location: Optional[str] = ""

# Core Prediction Logic
def run_prediction(req: PredictRequest):
    input_vector = np.zeros(len(symptom_cols))
    matched, unmatched, severities = [], [], []

    for s in req.symptoms:
        s_clean = s.strip().lower().replace(' ', '_')
        if s_clean in symptom_cols:
            input_vector[symptom_cols.index(s_clean)] = 1
            matched.append(s_clean.replace('_', ' ').title())
            severities.append({'symptom': s_clean.replace('_', ' ').title(),
                                'severity': severity_map.get(s_clean, 1)})
        else:
            unmatched.append(s)

    proba = model.predict_proba([input_vector])[0]
    top_idx = np.argsort(proba)[::-1][:3]
    top_disease = disease_classes[top_idx[0]]
    confidence  = round(float(proba[top_idx[0]]) * 100, 2)

    predictions = [
        {'disease': disease_classes[i], 'confidence': round(float(proba[i]) * 100, 2)}
        for i in top_idx
    ]

    exp = lime_explainer.explain_instance(input_vector, model.predict_proba, num_features=10)
    lime_reasons = [
        {'feature': feat.replace('_', ' ').title(),
         'impact': round(w, 4),
         'direction': 'Supports Diagnosis' if w > 0 else 'Against Diagnosis'}
        for feat, w in exp.as_list()
    ]

    avg_severity = round(np.mean([s['severity'] for s in severities]), 2) if severities else 0

    return {
        'patientName': req.patientName,
        'patientAge': req.patientAge,
        'patientGender': req.patientGender,
        'workerName': req.workerName,
        'location': req.location,
        'primaryDiagnosis': top_disease,
        'confidenceScore': confidence,
        'severityScore': avg_severity,
        'topPredictions': predictions,
        'matchedSymptoms': matched,
        'unmatchedSymptoms': unmatched,
        'symptomSeverities': severities,
        'description': description_map.get(top_disease, 'Description not available.'),
        'precautions': precaution_map.get(top_disease, []),
        'limeExplanation': lime_reasons,
    }


# API Routes
@app.get("/")
def root():
    return {"message": "ArogyaMitra ML API", "status": "running"}

@app.get("/symptoms")
def get_symptoms():
    """Returns list of all known symptoms."""
    return {"symptoms": [s.replace('_', ' ') for s in symptom_cols]}

@app.post("/predict")
def predict(req: PredictRequest):
    """Returns prediction as JSON."""
    if not req.symptoms:
        raise HTTPException(status_code=400, detail="At least one symptom is required")
    return run_prediction(req)

@app.post("/predict/pdf")
def predict_pdf(req: PredictRequest):
    """Returns prediction as a downloadable PDF report."""
    if not req.symptoms:
        raise HTTPException(status_code=400, detail="At least one symptom is required")

    data = run_prediction(req)
    pdf_bytes = generate_pdf(data)
    filename = f"ArogyaMitra_Report_{req.patientName.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
