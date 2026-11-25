"""Print the three highest RIASEC career suggestions for six area scores."""

import argparse
from pathlib import Path

import joblib
import numpy as np


MODEL_PATH = Path(__file__).resolve().parent / "riasec_model.joblib"


def main():
    parser = argparse.ArgumentParser(description="Sugerencias de carrera basadas en RIASEC.")
    parser.add_argument("--scores", required=True, help='Seis puntajes R,I,A,S,E,C separados por comas; ejemplo "0.8,0.9,0.5,0.6,0.4,0.5"')
    parser.add_argument("--topk", type=int, default=3)
    args = parser.parse_args()
    try:
        scores = np.array([float(value.strip()) for value in args.scores.split(",")])
    except ValueError:
        parser.error("Los puntajes deben ser números separados por comas.")
    if len(scores) != 6 or not np.isfinite(scores).all() or np.any(scores < 0.2) or np.any(scores > 1):
        parser.error("Se requieren seis puntajes R,I,A,S,E,C entre 0.2 y 1.0.")
    if args.topk < 1:
        parser.error("--topk debe ser positivo.")

    artifact = joblib.load(MODEL_PATH)
    model = artifact["model"]
    labels = artifact["career_labels"]
    probabilities = model.predict_proba(scores.reshape(1, -1))[0]
    order = np.argsort(-probabilities, kind="stable")
    for i in order[:args.topk]:
        code = str(model.classes_[i])
        print(f"{code}: {labels[code]} ({probabilities[i]:.3f})")
    print("Puntajes relativos basados en carrera declarada en RIASEC; no son probabilidades calibradas ni validan satisfacción futura.")


if __name__ == "__main__":
    main()
