# predict.py (versión verbose)
import argparse
import sys
import os
import joblib
import numpy as np
from pathlib import Path

print(">> predict.py iniciado", flush=True)

MODEL_PATH = Path("svm_model.joblib")
ENC_PATH   = Path("label_encoder.joblib")

def load_artifacts():
    print(f">> CWD: {os.getcwd()}", flush=True)
    print(f">> Buscando modelo en: {MODEL_PATH.resolve()}", flush=True)
    print(f">> Buscando encoder en: {ENC_PATH.resolve()}", flush=True)

    if not MODEL_PATH.exists():
        print("❌ No encuentro svm_model.joblib", flush=True)
        sys.exit(1)
    if not ENC_PATH.exists():
        print("❌ No encuentro label_encoder.joblib", flush=True)
        sys.exit(1)

    try:
        clf = joblib.load(MODEL_PATH)
        print("✅ Modelo cargado", flush=True)
    except Exception as e:
        print(f"❌ Error cargando modelo: {e}", flush=True)
        sys.exit(1)

    try:
        enc = joblib.load(ENC_PATH)
        print("✅ Encoder cargado", flush=True)
    except Exception as e:
        print(f"❌ Error cargando encoder: {e}", flush=True)
        sys.exit(1)

    return clf, enc

def parse_scores(scores_str: str) -> np.ndarray:
    print(f">> Raw scores: {scores_str}", flush=True)
    try:
        vals = [float(x.strip()) for x in scores_str.split(",")]
    except ValueError:
        print("❌ Los puntajes deben ser números (usa comas). Ej: 4,3,5,2,4,3,2,4,3", flush=True)
        sys.exit(1)
    if len(vals) != 9:
        print(f"❌ Debes pasar exactamente 9 valores. Recibí {len(vals)}.", flush=True)
        sys.exit(1)
    arr = np.array(vals, dtype=float).reshape(1, -1)
    print(f">> Vector de entrada: {arr.tolist()}", flush=True)
    return arr

def main():
    print(">> main() arrancando", flush=True)
    parser = argparse.ArgumentParser(
        description="Clasificación con SVM entrenado (9 puntajes)."
    )
    parser.add_argument(
        "--scores",
        required=True,
        help='Nueve números separados por comas. Ej: "4,3,5,2,4,3,2,4,3"'
    )
    parser.add_argument("--topk", type=int, default=3)
    args = parser.parse_args()
    print(">> Argumentos parseados", flush=True)

    X = parse_scores(args.scores)
    clf, enc = load_artifacts()

    # Pred
    try:
        pred_idx = clf.predict(X)[0]
        pred_lbl = enc.inverse_transform([pred_idx])[0]
        print(f"✅ Predicción: {pred_lbl} (índice: {pred_idx})", flush=True)
    except Exception as e:
        print(f"❌ Error en predict(): {e}", flush=True)
        sys.exit(1)

    # Probabilidades (si hay)
    try:
        if hasattr(clf, "predict_proba"):
            proba = clf.predict_proba(X)[0]
            order = np.argsort(proba)[::-1]
            k = max(1, min(args.topk, proba.shape[0]))
            print("\nTop probabilidades:", flush=True)
            for i in order[:k]:
                lbl = enc.inverse_transform([i])[0]
                print(f"  - {lbl:>20s}: {proba[i]:.4f}", flush=True)
        else:
            print("(ℹ️ Este modelo no expone predict_proba)", flush=True)
    except Exception as e:
        print(f"❌ Error en predict_proba(): {e}", flush=True)
        # no hacemos exit, ya imprimimos la clase

if __name__ == "__main__":
    main()
