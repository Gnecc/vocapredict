import os

import joblib
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path

MODEL_PATH = Path("svm_model.joblib")
ENC_PATH   = Path("label_encoder.joblib")

clf = joblib.load(MODEL_PATH)
enc = joblib.load(ENC_PATH)

app = FastAPI(title="Clasificador de Carreras", version="1.0")

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:8100,https://ionic-react-quiz-app.fly.dev",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Scores(BaseModel):
    scores: list[float]

@app.post("/predict")
def predict(data: Scores):
    vals = np.array(data.scores, dtype=float).reshape(1, -1)
    pred_idx = clf.predict(vals)[0]
    pred_lbl = enc.inverse_transform([pred_idx])[0]

    response = {"prediction": pred_lbl, "index": int(pred_idx)}

    if hasattr(clf, "predict_proba"):
        proba = clf.predict_proba(vals)[0]
        response["probabilities"] = {
            enc.inverse_transform([i])[0]: float(p)
            for i, p in enumerate(proba)
        }

    return response
