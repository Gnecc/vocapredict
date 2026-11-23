"""Train the 40- and 47-career models with a common holdout."""

import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from models.riasec import BACKEND_DIR, DATASET, FEATURES, SPLIT_SEED, fit_classifier


def load_profiles(path):
    data = pd.read_csv(path, low_memory=False)
    rows = data.loc[
        data["source"].eq("openpsychometrics_riasec")
        & data["instrument"].eq("RIASEC")
        & data["riasec_eligible"].eq(1)
    ].set_index("source_row_id")
    if not rows.index.is_unique:
        raise ValueError(f"Identificadores de origen duplicados en {path}")
    scores = rows.loc[:, FEATURES].to_numpy(dtype=float)
    if not np.isfinite(scores).all() or np.any((scores < 0.2) | (scores > 1)):
        raise ValueError(f"Puntajes RIASEC inválidos en {path}")
    return rows


def split(rows):
    return train_test_split(
        rows, test_size=0.2, stratify=rows["career_code"], random_state=SPLIT_SEED,
    )


def train(rows):
    return fit_classifier(rows.loc[:, FEATURES].to_numpy(), rows["career_code"].to_numpy())


def results(model, rows, training):
    actual = rows["career_code"].to_numpy()
    probabilities = model.predict_proba(rows.loc[:, FEATURES].to_numpy())
    ranked = model.classes_[np.argsort(-probabilities, axis=1, kind="stable")[:, :3]]
    popular = training["career_code"].value_counts().index[:3]
    return pd.DataFrame({
        "career": actual,
        "top1": ranked[:, 0] == actual,
        "top3": (ranked == actual[:, None]).any(axis=1),
        "popular": np.isin(actual, popular),
    }, index=rows.index)


def percent(value):
    return f"{value:.1%}"


def comparison_split(baseline_path, dataset_path):
    base = load_profiles(baseline_path)
    expanded = load_profiles(dataset_path)
    codes = set(base["career_code"])
    expanded_codes = set(expanded["career_code"])
    if len(codes) != 40 or len(expanded_codes) != 47 or not codes < expanded_codes:
        raise ValueError("Se requieren 40 clases originales y siete nuevas.")
    columns = ["career_code", *FEATURES]
    if not base[columns].equals(expanded.reindex(base.index)[columns]):
        raise ValueError("La ampliación cambió los puntajes o etiquetas originales.")

    added = expanded.loc[~expanded.index.isin(base.index)]
    corrections = added.loc[added["career_code"].isin(codes)]
    if len(corrections) != 12 or not corrections["country"].eq("MX").all():
        raise ValueError("Se esperaban las 12 correcciones revisadas con código MX.")
    base_train, shared_test = split(base)
    new_train, new_test = split(added.loc[~added["career_code"].isin(codes)])
    expanded_train = pd.concat([base_train, new_train, corrections])
    if set(expanded_train.index) & (set(shared_test.index) | set(new_test.index)):
        raise ValueError("Se solapan entrenamiento y prueba.")
    return base_train, expanded_train, shared_test, new_test


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, default=DATASET)
    parser.add_argument("--report", type=Path, default=BACKEND_DIR / "docs/comparacion_riasec_40_47.md")
    parser.add_argument("--artifacts", type=Path, default=BACKEND_DIR / "artifacts")
    args = parser.parse_args()

    base_train, expanded_train, shared_test, new_test = comparison_split(args.baseline, args.dataset)
    expanded = pd.concat([expanded_train, shared_test, new_test])
    codes = set(base_train["career_code"])
    expanded_codes = set(expanded["career_code"])
    model40, model47 = train(base_train), train(expanded_train)

    hits40 = results(model40, shared_test, base_train)
    hits47 = results(model47, shared_test, expanded_train)
    new_hits = results(model47, new_test, expanded_train)
    all_hits = pd.concat([hits47, new_hits])
    names = expanded.set_index("career_code")["career_name"].to_dict()
    counts = expanded["career_code"].value_counts()

    lines = [
        "# Comparación RIASEC de 40 y 47 carreras",
        "",
        f"Los modelos se entrenaron con {len(base_train):,} y {len(expanded_train):,} casos.",
        f"Comparten {len(shared_test):,} casos de prueba originales. Para las siete clases nuevas",
        f"se reservaron otros {len(new_test):,} casos. Las 12 correcciones MX se usaron para",
        "entrenar la versión ampliada. Cada modelo usa los seis puntajes y el mismo",
        "clasificador con pesos de clase. El objetivo observado es la carrera declarada.",
        "",
        "| Modelo y prueba | Casos | Top 1 | Top 3 | Top 3 promedio por carrera | Top 3 por frecuencia |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for label, hits in (
        ("40 · compartida", hits40), ("47 · compartida", hits47),
        ("47 · nuevas", new_hits), ("47 · completa", all_hits),
    ):
        macro = hits.groupby("career")["top3"].mean().mean()
        lines.append(f"| {label} | {len(hits):,} | {percent(hits.top1.mean())} | "
                     f"{percent(hits.top3.mean())} | {percent(macro)} | {percent(hits.popular.mean())} |")

    lines += [
        "", "## Resultados por carrera", "",
        "Top 1 y Top 3 indican el porcentaje de casos de cada carrera en los que",
        "la etiqueta declarada apareció en primera posición o entre las tres primeras.",
        "Las siete clases nuevas solo se evalúan con el modelo de 47.",
        "",
        "| Carrera | Perfiles disponibles | Casos de prueba | Top 1 · 40 | Top 3 · 40 | Top 1 · 47 | Top 3 · 47 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    per40 = hits40.groupby("career")[["top1", "top3"]].mean()
    per47 = all_hits.groupby("career")[["top1", "top3"]].mean()
    support = all_hits["career"].value_counts()
    for code in sorted(expanded_codes, key=names.get):
        values40 = [percent(value) for value in per40.loc[code]] if code in codes else ["—", "—"]
        values47 = [percent(value) for value in per47.loc[code]]
        values = " | ".join(values40 + values47)
        lines.append(f"| {names[code]} | {counts[code]:,} | {support[code]:,} | {values} |")

    args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    args.artifacts.mkdir(parents=True, exist_ok=True)
    for count, model in ((40, model40), (47, model47)):
        joblib.dump({
            "model": model,
            "career_labels": {str(code): names[code] for code in model.classes_},
            "features": FEATURES,
            "label_type": "carrera_declarada",
        }, args.artifacts / f"riasec_model_{count}.joblib")
    print(args.report)


if __name__ == "__main__":
    main()
