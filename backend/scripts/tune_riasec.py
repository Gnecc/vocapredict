"""Select 47-career alternatives using training data, then score the original holdout."""

import argparse
from functools import partial
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

from models.riasec import BACKEND_DIR, DATASET, FEATURES, SPLIT_SEED
from scripts.compare_riasec import comparison_split, percent, results, train


def logistic(rows, degree, power):
    y = rows["career_code"]
    counts = y.value_counts()
    weight = (len(y) / (len(counts) * y.map(counts).to_numpy())) ** power
    model = make_pipeline(
        StandardScaler(), PolynomialFeatures(degree=degree, include_bias=False),
        LogisticRegression(max_iter=500),
    )
    return model.fit(rows.loc[:, FEATURES].to_numpy(), y, logisticregression__sample_weight=weight)


def quadratic_discriminant(rows, power):
    y = rows["career_code"]
    priors = y.value_counts().sort_index().to_numpy(dtype=float) ** (1 - power)
    model = QuadraticDiscriminantAnalysis(priors=priors / priors.sum(), reg_param=0.1)
    return model.fit(rows.loc[:, FEATURES].to_numpy(), y)


def by_career(hits):
    return hits.groupby("career").agg(
        top1=("top1", "mean"), top3=("top3", "mean"), n=("top3", "size"),
        hits3=("top3", "sum"),
    )


def summary(hits):
    classes = by_career(hits)
    return (
        len(hits), percent(hits.top1.mean()), percent(hits.top3.mean()),
        percent(classes.top3.mean()), int(classes.hits3.eq(0).sum()),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, default=DATASET)
    args = parser.parse_args()
    base_train, expanded_train, shared_test, new_test = comparison_split(args.baseline, args.dataset)
    names = expanded_train.set_index("career_code")["career_name"].to_dict()
    original = set(base_train["career_code"])
    # Select on macro top 3. The balanced variant also limits the loss in
    # aggregate top 3 on the shared classes to three points in validation.
    tolerance = 0.03
    baseline = "47 original"
    candidates = {baseline: train}
    for power in (0.4, 0.6, 0.8, 1.0):
        candidates[f"Logística grado 1, peso {power:g}"] = partial(logistic, degree=1, power=power)
        candidates[f"Logística grado 2, peso {power:g}"] = partial(logistic, degree=2, power=power)
        candidates[f"Discriminante cuadrático, peso {power:g}"] = partial(quadratic_discriminant, power=power)

    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=SPLIT_SEED)
    folds = list(cv.split(expanded_train, expanded_train["career_code"]))
    validation = {}
    for name, fit in candidates.items():
        predictions = []
        for fit_indices, val_indices in folds:
            fit_rows = expanded_train.iloc[fit_indices]
            val_rows = expanded_train.iloc[val_indices]
            predictions.append(results(fit(fit_rows), val_rows, fit_rows))
        validation[name] = pd.concat(predictions)

    def shared_top3(hits):
        return hits.loc[hits.career.isin(original), "top3"].mean()

    def ranking(name):
        hits = validation[name]
        classes = by_career(hits)
        return classes.top3.mean(), -classes.hits3.eq(0).sum(), hits.top3.mean()

    threshold = shared_top3(validation[baseline]) - tolerance
    balanced = max(
        (name for name, hits in validation.items() if shared_top3(hits) >= threshold),
        key=ranking,
    )
    macro = max(candidates, key=ranking)
    selected = {"47 equilibrado": balanced, "47 énfasis por carrera": macro}
    if balanced == macro:
        selected.pop("47 énfasis por carrera")

    artifacts = BACKEND_DIR / "artifacts"
    artifacts.mkdir(exist_ok=True)
    runs = {"40 original": (train(base_train), base_train),
            baseline: (train(expanded_train), expanded_train)}
    for variant, candidate in selected.items():
        model = candidates[candidate](expanded_train)
        runs[variant] = (model, expanded_train)
        suffix = "equilibrado" if variant == "47 equilibrado" else "macro"
        joblib.dump({
            "model": model, "career_labels": {code: names[code] for code in model.classes_},
            "features": FEATURES, "label_type": "carrera_declarada",
        }, artifacts / f"riasec_model_47_{suffix}.joblib")

    lines = [
        "# Ajustes del predictor RIASEC de 47 carreras", "",
        "La selección usó tres pliegues estratificados dentro del entrenamiento.",
        "Se eligió por el promedio del top 3 de las 47 carreras. La variante equilibrada",
        "también limita a tres puntos porcentuales la caída del top 3 global de las",
        "carreras compartidas durante la validación interna. El umbral es una decisión",
        "para explorar el compromiso entre cobertura y aciertos globales.",
        "Se conservaron los 8,083 casos compartidos y los 385 nuevos de la prueba anterior.",
        "La prueba ya se había descrito en el informe anterior y sigue siendo exploratoria.",
        "",
        "Para reproducir desde `backend/` con el CSV histórico de 40 clases:",
        "",
        "```bash",
        "python3 -m scripts.tune_riasec --baseline /ruta/al/csv-historico.csv",
        "```",
        "", "## Validación interna", "",
        "| Configuración | Top 3 compartidas | Top 3 promedio por carrera | Carreras en cero |",
        "|---|---:|---:|---:|",
    ]
    for name, hits in validation.items():
        classes = by_career(hits)
        lines.append(f"| {name} | {percent(shared_top3(hits))} | "
                     f"{percent(classes.top3.mean())} | {classes.hits3.eq(0).sum()} |")
    lines += [""] + [f"- **{variant}** usa {candidate}." for variant, candidate in selected.items()]
    lines += [
        "", "## Misma partición de prueba", "",
        "| Modelo | Grupo | Casos | Top 1 | Top 3 | Top 3 promedio por carrera | Carreras en cero |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    per_run = {}
    for name, (model, training) in runs.items():
        shared_hits = results(model, shared_test, training)
        new_hits = results(model, new_test, training)
        complete = pd.concat([shared_hits, new_hits])
        per_run[name] = by_career(complete)
        for group, hits in (("compartidas", shared_hits), ("nuevas", new_hits), ("todas", complete)):
            values = " | ".join(map(str, summary(hits)))
            lines.append(f"| {name} | {group} | {values} |")
    headers = " | ".join(runs)
    lines += [
        "", "## Top 3 por carrera", "",
        "Cada celda muestra aciertos sobre el número de casos de prueba.",
        "El modelo de 40 carece de las siete clases nuevas.", "",
        f"| Carrera | {headers} |",
        "|---|" + "---:|" * len(runs),
    ]
    for code in sorted(names, key=names.get):
        scores = [
            "—" if name == "40 original" and code not in original else
            f"{metrics.loc[code, 'hits3']}/{metrics.loc[code, 'n']}"
            for name, metrics in per_run.items()
        ]
        lines.append(f"| {names[code]} | " + " | ".join(scores) + " |")
    report = BACKEND_DIR / "docs" / "ajustes_riasec_47.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
