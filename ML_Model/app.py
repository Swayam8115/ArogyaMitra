# ============================================================
# AROGYAMITRA — ML INFERENCE API
# ============================================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

import joblib
import numpy as np
import pandas as pd
import os
import re

import lime.lime_tabular


# ============================================================
# MODEL PATH
# ============================================================

MODEL_DIR = os.path.join(
    os.path.dirname(__file__),
    "model"
)

MODEL_FILE = os.path.join(
    MODEL_DIR,
    "disease_model.pkl"
)

LABEL_ENCODER_FILE = os.path.join(
    MODEL_DIR,
    "label_encoder.pkl"
)

SYMPTOM_COLUMNS_FILE = os.path.join(
    MODEL_DIR,
    "symptom_columns.pkl"
)

X_TRAIN_FILE = os.path.join(
    MODEL_DIR,
    "X_train.pkl"
)

SEVERITY_FILE = os.path.join(
    MODEL_DIR,
    "severity_map.pkl"
)

DESCRIPTION_FILE = os.path.join(
    MODEL_DIR,
    "description_map.pkl"
)

PRECAUTION_FILE = os.path.join(
    MODEL_DIR,
    "precaution_map.pkl"
)


# ============================================================
# CHECK MODEL FILES
# ============================================================

required_files = [
    MODEL_FILE,
    LABEL_ENCODER_FILE,
    SYMPTOM_COLUMNS_FILE,
    X_TRAIN_FILE
]

for file_path in required_files:
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Required model artifact not found: {file_path}"
        )


# ============================================================
# LOAD MODEL ARTIFACTS
# ============================================================

print("Loading ArogyaMitra ML model...")
model = joblib.load(MODEL_FILE)
label_encoder = joblib.load(
    LABEL_ENCODER_FILE
)

symptom_cols = joblib.load(
    SYMPTOM_COLUMNS_FILE
)

X_train = joblib.load(
    X_TRAIN_FILE
)

disease_classes = list(
    label_encoder.classes_
)


# ============================================================
# LOAD OPTIONAL METADATA
# ============================================================

if os.path.exists(SEVERITY_FILE):
    severity_map = joblib.load(SEVERITY_FILE)
else:
    severity_map = {}


if os.path.exists(DESCRIPTION_FILE):
    description_map = joblib.load(DESCRIPTION_FILE)
else:
    description_map = {}


if os.path.exists(PRECAUTION_FILE):
    precaution_map = joblib.load(PRECAUTION_FILE)
else:
    precaution_map = {}


# ============================================================
# LIME EXPLAINER
# ============================================================

lime_explainer = lime.lime_tabular.LimeTabularExplainer(
    training_data=X_train,
    feature_names=symptom_cols,
    class_names=disease_classes,
    mode="classification",
    random_state=42
)


print("✅ Model loaded successfully")
print(f"   Diseases : {len(disease_classes)}")
print(f"   Symptoms : {len(symptom_cols)}")


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="ArogyaMitra ML API",
    version="1.0.0"
)

# Enable CORS for all origins (frontend may run on a different port)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST SCHEMA
# ============================================================

class PredictRequest(BaseModel):
    symptoms: List[str]
    patientName: Optional[str] = "Patient"
    patientAge: Optional[int] = None
    patientGender: Optional[str] = None
    workerName: Optional[str] = "Healthcare Worker"
    location: Optional[str] = ""


# ============================================================
# SYMPTOM NORMALIZATION
# ============================================================

def clean_feature_name(name):
    name = str(name).strip().lower()
    name = name.replace("-", "_")
    name = re.sub(
        r"\s+",
        "_",
        name
    )
    name = re.sub(
        r"_+",
        "_",
        name
    )
    return name


# ============================================================
# CORE PREDICTION
# ============================================================

def run_prediction(req: PredictRequest):

    input_vector = np.zeros(
        len(symptom_cols),
        dtype=np.float32
    )

    matched = []
    unmatched = []

    # --------------------------------------------------------
    # MATCH SYMPTOMS
    # --------------------------------------------------------

    for symptom in req.symptoms:

        clean_symptom = clean_feature_name(
            symptom
        )
        if clean_symptom in symptom_cols:
            index = symptom_cols.index(
                clean_symptom
            )
            input_vector[index] = 1
            matched.append(
                clean_symptom
            )
        else:
            unmatched.append(
                symptom
            )

    # --------------------------------------------------------
    # ENSURE AT LEAST ONE SYMPTOM MATCHED
    # --------------------------------------------------------

    if not matched:
        raise HTTPException(
            status_code=400,
            detail="None of the provided symptoms are recognized."
        )

    # --------------------------------------------------------
    # CREATE DATAFRAME
    # --------------------------------------------------------

    input_df = pd.DataFrame(
        [input_vector],
        columns=symptom_cols
    )

    # --------------------------------------------------------
    # PREDICTION
    # --------------------------------------------------------
    proba = model.predict_proba(
        input_df
    )[0]

    # --------------------------------------------------------
    # TOP 3 PREDICTIONS
    # --------------------------------------------------------

    top_idx = np.argsort(
        proba
    )[::-1][:3]

    top_disease = disease_classes[
        top_idx[0]
    ]

    confidence = round(
        float(proba[top_idx[0]]) * 100,
        2
    )

    predictions = [
        {
            "disease": disease_classes[i],
            "confidence": round(
                float(proba[i]) * 100,
                2
            )
        }
        for i in top_idx
    ]


    # --------------------------------------------------------
    # LIME EXPLANATION
    # --------------------------------------------------------

    exp = lime_explainer.explain_instance(
        input_vector,
        model.predict_proba,
        num_features=10
    )

    lime_reasons = [
        {
            "feature": feature.replace(
                "_",
                " "
            ).title(),
            "impact": round(
                float(weight),
                4
            ),
            "direction": (
                "Supports Diagnosis"
                if weight > 0
                else "Against Diagnosis"
            )
        }
        for feature, weight in exp.as_list()
    ]


    # --------------------------------------------------------
    # SEVERITY
    # --------------------------------------------------------

    # Currently unavailable because the trained model
    # does not have a valid symptom-severity mapping.
    severity_score = None
    symptom_severities = []

    # --------------------------------------------------------
    # DESCRIPTION
    # --------------------------------------------------------

    description = description_map.get(
        top_disease,
        "Description not available."
    )

    # --------------------------------------------------------
    # PRECAUTIONS
    # --------------------------------------------------------

    precautions = precaution_map.get(
        top_disease,
        []
    )

    # --------------------------------------------------------
    # FINAL RESPONSE
    # --------------------------------------------------------
    return {
        "patientName": req.patientName,
        "patientAge": req.patientAge,
        "patientGender": req.patientGender,
        "workerName": req.workerName,
        "location": req.location,
        "primaryDiagnosis": top_disease,
        "confidenceScore": confidence,
        "severityScore": severity_score,
        "topPredictions": predictions,
        "matchedSymptoms": [
            symptom.replace(
                "_",
                " "
            ).title()

            for symptom in matched
        ],

        "unmatchedSymptoms": unmatched,
        "symptomSeverities": symptom_severities,
        "description": description,
        "precautions": precautions,
        "limeExplanation": lime_reasons
    }


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "ArogyaMitra ML API",
        "status": "running"
    }


# ============================================================
# SYMPTOMS ENDPOINT
# ============================================================

@app.get("/symptoms")
def get_symptoms():
    return {
        "symptoms": [
            symptom.replace(
                "_",
                " "
            )
            for symptom in symptom_cols
        ]
    }

# ============================================================
# PREDICTION ENDPOINT
# ============================================================

@app.post("/predict")
def predict(
    req: PredictRequest
):

    if not req.symptoms:
        raise HTTPException(
            status_code=400,
            detail="At least one symptom is required."
        )
    return run_prediction(req)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=True)