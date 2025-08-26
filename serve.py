# serve.py
import joblib
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path

# Paths a tus artefactos
MODEL_PATH = Path("svm_model.joblib")
ENC_PATH   = Path("label_encoder.joblib")

# Cargar modelo y encoder
clf = joblib.load(MODEL_PATH)
enc = joblib.load(ENC_PATH)

# Inicializar FastAPI
app = FastAPI(title="Clasificador de Carreras", version="1.0")

# Definir request body
class Scores(BaseModel):
    scores: list[float]   # Deben ser 9 valores

@app.post("/predict")
def predict(data: Scores):
    vals = np.array(data.scores, dtype=float).reshape(1, -1)
    pred_idx = clf.predict(vals)[0]
    pred_lbl = enc.inverse_transform([pred_idx])[0]

    response = {"prediction": pred_lbl, "index": int(pred_idx)}

    # Si hay probabilidades
    if hasattr(clf, "predict_proba"):
        proba = clf.predict_proba(vals)[0]
        response["probabilities"] = {
            enc.inverse_transform([i])[0]: float(p)
            for i, p in enumerate(proba)
        }

    return response
