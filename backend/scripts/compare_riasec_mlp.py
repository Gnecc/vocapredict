"""Train and compare neural networks on the historical 40-career split."""

import argparse
from pathlib import Path

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler

from models.riasec import BACKEND_DIR, FEATURES, SPLIT_SEED
from scripts.benchmark_riasec_40 import respuestas_originales
from scripts.compare_riasec import load_profiles, percent, split, train
from scripts.prepare_riasec_dataset import QUESTIONS


CONFIGS = (((32,), 0.01), ((64, 32), 0.1), ((128, 64), 1.0))
MAX_EPOCHS = 65
PATIENCE = 10


def metrics(probabilities, actual):
    ranked = np.argsort(-probabilities, axis=1, kind="stable")[:, :3]
    hit1 = ranked[:, 0] == actual
    hit3 = (ranked == actual[:, None]).any(axis=1)
    recall = [hit1[actual == label].mean() for label in np.unique(actual)]
    return hit1.mean(), hit3.mean(), float(np.mean(recall))


def new_network(layers, alpha):
    return MLPClassifier(hidden_layer_sizes=layers, alpha=alpha, batch_size=256,
                         random_state=SPLIT_SEED)


def choose_network(x_fit, y_fit, x_val, y_val, classes):
    candidates = []
    for layers, alpha in CONFIGS:
        net = new_network(layers, alpha)
        best = (-1.0, -1.0, -1.0)
        best_epoch = 0
        for epoch in range(1, MAX_EPOCHS + 1):
            net.partial_fit(x_fit, y_fit, classes=classes)
            score = metrics(net.predict_proba(x_val), y_val)
            if score > best:
                best, best_epoch = score, epoch
            if epoch - best_epoch >= PATIENCE:
                break
        candidates.append((layers, alpha, best_epoch, best))
    return max(candidates, key=lambda item: item[-1]), candidates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--raw-riasec", type=Path, required=True)
    args = parser.parse_args()

    rows = load_profiles(args.baseline)
    full, test = split(rows)
    fit, val = split(full)
    if rows.career_code.nunique() != 40 or not full.index.intersection(test.index).empty:
        raise ValueError("Se necesita la partición original de 40 clases sin filas compartidas.")
    items = respuestas_originales(args.raw_riasec, rows)
    features = rows.loc[:, FEATURES].join(items)
    encoder = LabelEncoder().fit(full.career_code)
    y_fit, y_val, y_full, y_test = (
        encoder.transform(group.career_code) for group in (fit, val, full, test)
    )
    classes = np.arange(len(encoder.classes_))

    active = train(full)
    if not np.array_equal(active.classes_, encoder.classes_):
        raise ValueError("Las clases de la línea base no coinciden.")
    active_metrics = metrics(active.predict_proba(test.loc[:, FEATURES].to_numpy()), y_test)
    item_scaler = StandardScaler().fit(items.loc[full.index])
    logistic = LogisticRegression(max_iter=600).fit(item_scaler.transform(items.loc[full.index]), y_full)
    logistic_metrics = metrics(logistic.predict_proba(item_scaler.transform(items.loc[test.index])), y_test)
    results = [("Logística activa", "6 puntajes", active_metrics),
               ("Logística regularizada", "48 respuestas", logistic_metrics)]
    validation = []

    artifacts = BACKEND_DIR / "artifacts"
    artifacts.mkdir(exist_ok=True)
    for name, columns in (
        ("6 puntajes", list(FEATURES)), ("48 respuestas", QUESTIONS),
        ("48 respuestas + 6 puntajes", QUESTIONS + list(FEATURES)),
    ):
        x_fit, x_val, x_full, x_test = (
            features.loc[group.index, columns].to_numpy()
            for group in (fit, val, full, test)
        )
        fitted_scaler = StandardScaler().fit(x_fit)
        selected, candidates = choose_network(
            fitted_scaler.transform(x_fit), y_fit, fitted_scaler.transform(x_val), y_val, classes,
        )
        validation.extend((name, *item, item == selected) for item in candidates)
        layers, alpha, epochs, _ = selected
        scaler = StandardScaler().fit(x_full)
        network = new_network(layers, alpha)
        scaled_full = scaler.transform(x_full)
        for _ in range(epochs):
            network.partial_fit(scaled_full, y_full, classes=classes)
        score = metrics(network.predict_proba(scaler.transform(x_test)), y_test)
        results.append(("Red neuronal MLP", name, score))
        joblib.dump({"model": network, "scaler": scaler, "encoder": encoder,
                     "features": columns}, artifacts / f"riasec_mlp_{len(columns)}.joblib")
        print(f"{name}: {percent(score[0])}", flush=True)

    lines = [
        "# Redes neuronales RIASEC de 40 carreras", "",
        f"Prueba histórica de {len(test):,} casos. Se comparan las seis escalas, las 48",
        "respuestas y ambas representaciones juntas. Las respuestas se verificaron",
        "recalculando los seis puntajes. Se eligieron arquitectura, regularización y",
        f"época en los {len(val):,} casos de validación interna por primera opción,",
        "con top 3 y exactitud equilibrada para desempatar. La red se reentrenó con",
        "todos los casos de entrenamiento durante el número de épocas elegido.",
        "La partición de prueba se reutiliza. Los resultados son exploratorios.", "",
        "| Modelo | Entrada | Primera opción | Top 3 | Exactitud equilibrada |",
        "|---|---|---:|---:|---:|",
    ]
    for name, inputs, score in results:
        lines.append(f"| {name} | {inputs} | " + " | ".join(map(percent, score)) + " |")
    lines += [
        "", "## Selección en validación", "",
        "| Entrada | Capas ocultas | Regularización | Época | Primera opción | Top 3 | Exactitud equilibrada | Elegida |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for name, layers, alpha, epochs, score, selected in validation:
        lines.append(f"| {name} | {layers} | {alpha:g} | {epochs} | " +
                     " | ".join(map(percent, score)) + f" | {'Sí' if selected else '—'} |")
    lines += [
        "", "Ejecutar desde `backend/` con el CSV histórico de 40 clases y el TSV original:", "",
        "```bash",
        "python3 -m scripts.compare_riasec_mlp --baseline /ruta/al/csv-historico.csv --raw-riasec /ruta/al/data.csv",
        "```",
    ]
    report = BACKEND_DIR / "docs" / "redes_neuronales_riasec_40.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
