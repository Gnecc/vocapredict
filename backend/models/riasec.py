"""Training and holdout evaluation for the RIASEC declared-major model."""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


BACKEND_DIR = Path(__file__).resolve().parents[1]
DATASET = BACKEND_DIR / "data" / "vocapredict_unificado_riasec.csv"
MODEL = BACKEND_DIR / "riasec_model.joblib"
METRICS = BACKEND_DIR / "artifacts" / "riasec_metrics.json"
FEATURES = tuple(f"riasec_{area}" for area in "RIASEC")
MIN_COUNTRY_TEST_ROWS = 50
CLASS_WEIGHT_POWER = 0.6
SPLIT_SEED = 20261015


def fit_classifier(scores, labels):
    labels = pd.Series(labels, dtype=str)
    counts = labels.value_counts()
    inverse_frequency = len(labels) / (len(counts) * labels.map(counts).to_numpy())
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=500))
    model.fit(scores, labels.to_numpy(), logisticregression__sample_weight=(
        inverse_frequency ** CLASS_WEIGHT_POWER
    ))
    return model


def _top_k_rate(actual: np.ndarray, probabilities: np.ndarray, classes: np.ndarray, k: int) -> float:
    top_indices = np.argsort(probabilities, axis=1)[:, -k:]
    top_labels = classes[top_indices]
    return float(np.mean(np.any(top_labels == actual[:, None], axis=1)))


def run(dataset_path: str | Path = DATASET) -> dict:
    path = Path(dataset_path)
    data = pd.read_csv(path, low_memory=False)
    required = {"source", "instrument", "riasec_eligible", "career_code", "career_name", "country", *FEATURES}
    missing = sorted(required.difference(data.columns))
    if missing:
        raise ValueError(f"Faltan columnas del dataset unificado: {', '.join(missing)}")

    eligible = data.loc[
        (data["source"] == "openpsychometrics_riasec")
        & (data["instrument"] == "RIASEC")
        & (pd.to_numeric(data["riasec_eligible"], errors="coerce") == 1)
    ].copy()
    if eligible.empty:
        raise ValueError("No hay filas RIASEC elegibles para entrenar.")

    scores = eligible.loc[:, FEATURES].apply(pd.to_numeric, errors="coerce")
    valid_scores = np.isfinite(scores.to_numpy(dtype=float)).all(axis=1)
    valid_scores &= scores.ge(0.2).all(axis=1).to_numpy()
    valid_scores &= scores.le(1.0).all(axis=1).to_numpy()
    valid_label = eligible["career_code"].notna() & eligible["career_name"].notna()
    invalid_count = int((~(valid_scores & valid_label.to_numpy())).sum())
    if invalid_count:
        raise ValueError(f"Hay {invalid_count} filas marcadas elegibles con puntajes o carrera inválidos.")

    labels = (
        eligible[["career_code", "career_name"]]
        .drop_duplicates()
        .sort_values("career_code")
    )
    if labels["career_code"].duplicated().any():
        raise ValueError("Un código de carrera corresponde a más de un nombre.")
    career_labels = dict(zip(labels["career_code"], labels["career_name"]))
    counts = eligible["career_code"].value_counts().sort_index()
    if len(counts) < 4 or counts.min() < 5:
        raise ValueError("Se necesitan al menos 4 carreras y 5 filas por carrera para dividir datos.")

    indices = np.arange(len(eligible))
    train_idx, test_idx = train_test_split(
        indices,
        test_size=0.2,
        stratify=eligible["career_code"].to_numpy(),
        random_state=SPLIT_SEED,
    )
    x = scores.to_numpy(dtype=float)
    y = eligible["career_code"].to_numpy(dtype=str)
    model = fit_classifier(x[train_idx], y[train_idx])
    probabilities = model.predict_proba(x[test_idx])
    classes = model.classes_
    predictions = classes[np.argmax(probabilities, axis=1)]
    top3_labels = classes[np.argsort(-probabilities, axis=1)[:, :3]]

    report = classification_report(
        y[test_idx], predictions, labels=classes, output_dict=True, zero_division=0
    )
    by_country = {}
    country = eligible["country"].fillna("").astype(str).to_numpy()[test_idx]
    for code in sorted(set(country)):
        mask = country == code
        if len(code) != 2 or not code.isalpha() or mask.sum() < MIN_COUNTRY_TEST_ROWS:
            continue
        by_country[code] = {
            "test_rows": int(mask.sum()),
            "accuracy_declared_major": float(accuracy_score(y[test_idx][mask], predictions[mask])),
            "top3_declared_major": _top_k_rate(y[test_idx][mask], probabilities[mask], classes, 3),
        }

    metrics = {
        "evaluation_target": "carrera declarada (major), no satisfacción con la recomendación",
        "dataset": str(path),
        "source_rows": int(len(data)),
        "riasec_eligible_rows": int(len(eligible)),
        "train_rows": int(len(train_idx)),
        "test_rows": int(len(test_idx)),
        "features": list(FEATURES),
        "normalization": "mean of eight 1–5 responses per area divided by 5",
        "train_class_weight_power": CLASS_WEIGHT_POWER,
        "score_note": "Relative model score after class weighting; not a calibrated probability of career fit.",
        "career_rows": {str(code): int(n) for code, n in counts.items()},
        "career_labels": career_labels,
        "accuracy_declared_major": float(accuracy_score(y[test_idx], predictions)),
        "balanced_accuracy_declared_major": float(balanced_accuracy_score(y[test_idx], predictions)),
        "top3_declared_major": _top_k_rate(y[test_idx], probabilities, classes, 3),
        "macro_top3_declared_major": float(np.mean([
            np.mean(np.any(top3_labels[y[test_idx] == code] == code, axis=1))
            for code in classes
        ])),
        "careers_seen_top1": int(len(set(predictions))),
        "careers_seen_top3": int(len(set(top3_labels.ravel()))),
        "per_career": {
            code: {
                metric: report[code][metric]
                for metric in ("precision", "recall", "f1-score", "support")
            }
            for code in classes
        },
        "country_holdout": by_country,
        "country_min_test_rows": MIN_COUNTRY_TEST_ROWS,
    }

    joblib.dump(
        {
            "model": model,
            "career_labels": career_labels,
            "features": FEATURES,
            "label_type": "carrera_declarada",
        },
        MODEL,
    )
    METRICS.parent.mkdir(exist_ok=True)
    METRICS.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: metrics[k] for k in ("riasec_eligible_rows", "train_rows", "test_rows", "accuracy_declared_major", "top3_declared_major")}, ensure_ascii=False, indent=2))
    print(f"Métricas completas: {METRICS}")
    return metrics
