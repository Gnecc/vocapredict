"""Compare the 40-career baseline against the same model with three added classes."""

import argparse
from pathlib import Path

import joblib
import pandas as pd

from models.riasec import BACKEND_DIR, DATASET, FEATURES
from scripts.compare_riasec import comparison_split, percent, results, train


ADDITIONAL_CODES = {"COM", "CIN", "TEA"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, default=DATASET)
    args = parser.parse_args()

    train40, train47, shared_test, test_new47 = comparison_split(args.baseline, args.dataset)
    additional_train = train47.loc[train47["career_code"].isin(ADDITIONAL_CODES)]
    additional_test = test_new47.loc[test_new47["career_code"].isin(ADDITIONAL_CODES)]
    train43 = pd.concat([train40, additional_train], verify_integrity=True)
    test43 = pd.concat([shared_test, additional_test], verify_integrity=True)
    if set(train43.index) & set(test43.index) or train43["career_code"].nunique() != 43:
        raise ValueError("La comparación requiere 43 clases sin solapamiento entre entrenamiento y prueba.")

    model40 = train(train40)
    model43 = train(train43)
    hits40 = results(model40, test43, train40)
    hits43 = results(model43, test43, train43)
    lines = [
        "# Comparación RIASEC de 40 y 43 carreras", "",
        "La versión de 43 agrega Comunicación, Cinematografía y Teatro. Ambos modelos",
        "usan los mismos perfiles de entrenamiento de las 40 clases originales y la",
        "misma regresión logística con pesos de clase. El predictor de 43 se entrena",
        f"con {len(train43):,} casos, incluidos {len(additional_train):,} de las tres clases nuevas.",
        "Las 12 correcciones del conjunto de 47 quedaron fuera de este experimento",
        "para medir específicamente el efecto de añadir las tres clases.",
        "Los conjuntos de prueba conservan los identificadores de la comparación anterior.",
        "Las tres carreras se eligieron con resultados de esa misma prueba, así que",
        "el resultado es exploratorio y requiere una evaluación nueva para confirmarse.", "",
        "| Modelo | Grupo | Casos | Top 1 | Top 3 | Top 3 promedio por carrera | Carreras con cero en top 3 |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for classes, hits in ((40, hits40), (43, hits43)):
        for title, group in (
            ("Compartidas", hits.loc[shared_test.index]),
            ("Nuevas", hits.loc[additional_test.index]),
            ("Todas", hits),
        ):
            by_career = group.groupby("career")["top3"].mean()
            lines.append(
                f"| {classes} | {title} | {len(group):,} | {percent(group.top1.mean())} | "
                f"{percent(group.top3.mean())} | {percent(by_career.mean())} | {by_career.eq(0).sum()} |"
            )

    names = train43.set_index("career_code")["career_name"].to_dict()
    lines += [
        "", "## Resultados por carrera", "",
        "Cada celda indica aciertos sobre el total de casos de prueba de esa carrera.",
        "El modelo de 40 carece de las tres clases nuevas.", "",
        "| Carrera | Top 1 · 40 | Top 3 · 40 | Top 1 · 43 | Top 3 · 43 |",
        "|---|---:|---:|---:|---:|",
    ]
    grouped40 = hits40.groupby("career").agg(top1=("top1", "sum"), top3=("top3", "sum"), n=("top3", "size"))
    grouped43 = hits43.groupby("career").agg(top1=("top1", "sum"), top3=("top3", "sum"), n=("top3", "size"))
    for code in sorted(names, key=names.get):
        before = grouped40.loc[code]
        after = grouped43.loc[code]
        scores40 = ["—", "—"] if code in ADDITIONAL_CODES else [
            f"{before.top1}/{before.n}", f"{before.top3}/{before.n}",
        ]
        scores = scores40 + [f"{after.top1}/{after.n}", f"{after.top3}/{after.n}"]
        lines.append(f"| {names[code]} | " + " | ".join(scores) + " |")

    report = BACKEND_DIR / "docs" / "comparacion_riasec_40_43.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    artifacts = BACKEND_DIR / "artifacts"
    artifacts.mkdir(exist_ok=True)
    joblib.dump({
        "model": model43,
        "career_labels": names,
        "features": FEATURES,
        "label_type": "carrera_declarada",
    }, artifacts / "riasec_model_43.joblib")
    print(report)


if __name__ == "__main__":
    main()
