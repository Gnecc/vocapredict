import argparse
import json
import sys
from pathlib import Path

import numpy as np


MODEL_PATH = Path("artifacts/neural_network_model.npz")
LABELS_PATH = Path("artifacts/neural_network_labels.json")
EXPECTED_SCORE_COUNT = 9


def parse_scores(raw_scores: str) -> np.ndarray:
    try:
        scores = [float(value.strip()) for value in raw_scores.split(",")]
    except ValueError as error:
        raise ValueError("Los puntajes deben ser numeros separados por comas.") from error

    if len(scores) != EXPECTED_SCORE_COUNT:
        raise ValueError(
            f"Se requieren {EXPECTED_SCORE_COUNT} puntajes; se recibieron {len(scores)}."
        )

    return np.array(scores, dtype=float).reshape(1, -1)


def load_artifacts():
    missing = [str(path) for path in (MODEL_PATH, LABELS_PATH) if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Faltan artefactos de la red neuronal: "
            + ", ".join(missing)
            + ". Entrena primero con `python3 train.py --model nn`."
        )

    model = np.load(MODEL_PATH)
    labels = json.loads(LABELS_PATH.read_text())
    return model, labels


def relu(values: np.ndarray) -> np.ndarray:
    return np.maximum(values, 0)


def softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - np.max(values, axis=1, keepdims=True)
    exp_values = np.exp(shifted)
    return exp_values / np.sum(exp_values, axis=1, keepdims=True)


def predict_proba(model, scores: np.ndarray) -> np.ndarray:
    normalized = (scores - model["mean"]) / model["scale"]
    hidden_1 = relu(normalized @ model["weight_1"] + model["bias_1"])
    hidden_2 = relu(hidden_1 @ model["weight_2"] + model["bias_2"])
    logits = hidden_2 @ model["weight_3"] + model["bias_3"]
    return softmax(logits)[0]


def print_prediction(model, labels: list[str], scores: np.ndarray, topk: int):
    probabilities = predict_proba(model, scores)
    class_order = np.argsort(probabilities)[::-1]
    prediction_index = int(class_order[0])
    print(f"Prediccion: {labels[prediction_index]}")
    print(f"Indice: {prediction_index}")

    limit = max(1, min(topk, len(class_order)))
    print("Probabilidades:")
    for class_index in class_order[:limit]:
        print(f"  {labels[class_index]}: {probabilities[class_index]:.4f}")


def main():
    parser = argparse.ArgumentParser(
        description="Predice una carrera con la red neuronal hecha con numpy."
    )
    parser.add_argument(
        "--scores",
        required=True,
        help='Nueve puntajes separados por comas. Ej: "0.74,0.78,0.9,0.54,0.23,0.1,0.1,0.2,0.68"',
    )
    parser.add_argument("--topk", type=int, default=3)
    args = parser.parse_args()

    try:
        model, labels = load_artifacts()
        scores = parse_scores(args.scores)
        print_prediction(model, labels, scores, args.topk)
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
