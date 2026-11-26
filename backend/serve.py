"""RIASEC interest-based career suggestions API."""

import os
from pathlib import Path

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, StrictInt

if __package__:
    from .family_prediction import family_scores
    from .red_semantica.riasec_owl import NOMBRES, cargar_catalogo, inferir
else:
    from family_prediction import family_scores
    from red_semantica.riasec_owl import NOMBRES, cargar_catalogo, inferir

MODEL_PATH = Path(__file__).resolve().parent / "riasec_model.joblib"
artifact = joblib.load(MODEL_PATH)
clf = artifact["model"]
career_labels = artifact["career_labels"]
family_artifact = joblib.load(MODEL_PATH.with_name("riasec_families.joblib"))

semantic_catalog = cargar_catalogo()

app = FastAPI(title="VocaPredict RIASEC", version="2.0")

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:8100,http://127.0.0.1:3000,http://127.0.0.1:8100,https://vocapredict-frontend.fly.dev,https://ionic-react-quiz-app.fly.dev",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_methods=["*"],
    allow_headers=["*"],
)

class Scores(BaseModel):
    scores: list[float]
    answers: list[StrictInt] | None = None

@app.post("/predict")
def predict(data: Scores):
    if len(data.scores) != 6:
        raise HTTPException(status_code=422, detail="Se requieren seis puntajes en orden R, I, A, S, E, C.")
    vals = np.asarray(data.scores, dtype=float)
    if not np.isfinite(vals).all() or np.any(vals < 0.2) or np.any(vals > 1.0):
        raise HTTPException(status_code=422, detail="Los seis puntajes deben estar entre 0.2 y 1.0.")

    families = {}
    if data.answers is not None:
        answers = np.asarray(data.answers)
        if answers.shape != (48,) or np.any(answers < 1) or np.any(answers > 5):
            raise HTTPException(status_code=422, detail="Se requieren 48 respuestas enteras entre 1 y 5.")
        if not np.allclose(vals, answers.reshape(6, 8).mean(axis=1) / 5, rtol=0, atol=1e-6):
            raise HTTPException(status_code=422, detail="Los puntajes y las respuestas no coinciden.")
        scores = family_scores(family_artifact, [data.answers])[0]
        ranked = np.argsort(-scores, kind="stable")[:4]
        families["family_recommendations"] = [str(family_artifact["families"][i]) for i in ranked]

    probabilities = clf.predict_proba(vals.reshape(1, -1))[0]
    classes = clf.classes_
    order = np.argsort(-probabilities, kind="stable")
    best = str(classes[order[0]])
    if families:
        memberships = {
            str(code): family_artifact["families"][row.argmax()]
            for code, row in zip(family_artifact["grouped"].classes_, family_artifact["memberships"])
        }
        families["careers_by_family"] = {
            family: [
                career_labels[str(classes[i])]
                for i in order if memberships[str(classes[i])] == family
            ][:2]
            for family in families["family_recommendations"]
        }
    _, connections = inferir(semantic_catalog, vals)
    semantic_connections = [
        {
            "career_code": option["id"],
            "career_name": option["nombre"],
            "interests": [
                {"code": area, "name": NOMBRES[area], "score": float(score)}
                for area, score in evidence
            ],
        }
        for option, evidence in connections
    ]
    return {
        **families,
        "semantic_connections": semantic_connections,
        "prediction": best,
        "probabilities": {str(code): float(probabilities[i]) for i, code in enumerate(classes)},
        "recommendations": [
            {
                "career_code": str(classes[i]),
                "career_name": career_labels[str(classes[i])],
                "score": float(probabilities[i]),
            }
            for i in order[:3]
        ],
        "career_labels": career_labels,
        "model_basis": "Puntaje relativo basado en carreras declaradas por participantes de RIASEC; no es probabilidad calibrada ni mide satisfacción futura.",
    }
