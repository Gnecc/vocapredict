"""Tune the ranking of Comunicación y Periodismo on training folds only."""

import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold

from models.riasec import BACKEND_DIR, DATASET, FEATURES, SPLIT_SEED
from scripts.compare_riasec import percent, train
from scripts.compare_riasec_42 import GROUP, GROUP_NAME, MEMBERS, evaluate, evaluate_scores
from scripts.compare_riasec_43 import comparison_split_43


FACTORS = (1.0, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.6, 0.5)
MIN_RETAINED_HITS = 0.8


def counts(hits):
    group = hits.target.eq(GROUP)
    hits_group = int(hits.loc[group, "top3"].sum())
    offered = int(hits.shows_group.sum())
    precision = hits_group / offered if offered else 0.0
    return hits_group, offered, precision


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, default=DATASET)
    args = parser.parse_args()

    train40, train43, shared, new = comparison_split_43(args.baseline, args.dataset)
    train42 = train43.assign(career_code=train43.career_code.replace(MEMBERS))
    test = pd.concat([shared, new], verify_integrity=True)
    assert train42.career_code.nunique() == 42

    validation = {factor: [] for factor in FACTORS}
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=SPLIT_SEED)
    for fit_index, val_index in cv.split(train42, train42.career_code):
        model = train(train42.iloc[fit_index])
        # Keep the original labels for subsequent Communication/Journalism breakdowns.
        held = train43.iloc[val_index]
        raw = model.predict_proba(held.loc[:, FEATURES].to_numpy())
        for factor, folds in validation.items():
            folds.append(evaluate_scores(raw, model.classes_, held, group_multiplier=factor))
    metrics = {factor: counts(pd.concat(folds)) for factor, folds in validation.items()}
    floor = metrics[1.0][0] * MIN_RETAINED_HITS
    feasible = [factor for factor in FACTORS if metrics[factor][0] >= floor]
    chosen = max(feasible, key=lambda factor: (metrics[factor][2], metrics[factor][0]))

    model42 = train(train42)
    raw = model42.predict_proba(test.loc[:, FEATURES].to_numpy())
    comparisons = {
        "40 original": evaluate(train(train40), test),
        "42 original": evaluate_scores(raw, model42.classes_, test),
        "42 ajustado": evaluate_scores(raw, model42.classes_, test, group_multiplier=chosen),
    }
    before = comparisons["42 original"]
    after = comparisons["42 ajustado"]
    outside = ~before.target.eq(GROUP)
    if (before.loc[outside, "top3"] & ~after.loc[outside, "top3"]).any():
        raise AssertionError("El ajuste desplazó un acierto fuera de la clase agrupada.")

    lines = [
        "# Ajuste de precisión de Comunicación y Periodismo", "",
        f"La prueba reutiliza los {len(shared):,} casos compartidos y los {len(new):,} nuevos.",
        "En todos los modelos se mide la clase agrupada según la comparación anterior.",
        "El ajuste multiplica solo la puntuación de esa clase antes de ordenar las opciones.",
        "En tres pliegues internos se maximiza su precisión, conservando al menos",
        f"{percent(MIN_RETAINED_HITS)} de sus aciertos originales como decisión del experimento.",
        "El factor se eligió antes de ejecutar la evaluación de prueba, reutilizada",
        "de experimentos previos. Esta evaluación sigue siendo exploratoria.", "",
        "| Factor | Aciertos del grupo | Veces en top 3 | Precisión | Cumple el mínimo |",
        "|---:|---:|---:|---:|---|",
    ]
    for factor, (correct, offered, precision) in metrics.items():
        lines.append(f"| {factor:g} | {correct} | {offered} | {percent(precision)} | "
                     f"{'Sí' if factor in feasible else 'No'} |")
    lines += [
        "", f"Factor elegido **{chosen:g}×**.", "",
        "## Resultado en la misma partición", "",
        "| Modelo | Precisión del grupo | Periodismo original | Comunicación original | "
        "Top 3 compartidos | Top 3 fuera del grupo | Top 3 total |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, hits in comparisons.items():
        correct, offered, precision = counts(hits)
        jou = hits.loc[hits.source.eq("JOU"), "top3"]
        com = hits.loc[hits.source.eq("COM"), "top3"]
        lines.append(f"| {name} | {correct}/{offered} ({percent(precision)}) | "
                     f"{jou.sum()}/{len(jou)} | {com.sum()}/{len(com)} | "
                     f"{percent(hits.loc[shared.index, 'top3'].mean())} | "
                     f"{percent(hits.loc[outside, 'top3'].mean())} | {percent(hits.top3.mean())} |")

    names = train42.set_index("career_code")["career_name"].to_dict()
    names[GROUP] = GROUP_NAME
    lines += [
        "", "## Top 3 por clase", "",
        "| Clase | 40 original | 42 original | 42 ajustado |",
        "|---|---:|---:|---:|",
    ]
    grouped = [hits.groupby("target").top3.agg(["sum", "size"]) for hits in comparisons.values()]
    for code in sorted(names, key=names.get):
        cells = [f"{table.loc[code, 'sum']}/{table.loc[code, 'size']}" for table in grouped]
        lines.append(f"| {names[code]} | " + " | ".join(cells) + " |")
    lines += [
        "", "Para reproducir desde `backend/` con el CSV histórico de las 40 clases:", "",
        "```bash",
        "python3 -m scripts.tune_riasec_42 --baseline /ruta/al/csv-historico.csv",
        "```",
    ]
    report = BACKEND_DIR / "docs" / "ajuste_precision_riasec_42.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    artifacts = BACKEND_DIR / "artifacts"
    artifacts.mkdir(exist_ok=True)
    joblib.dump({
        "model": model42, "career_labels": names, "features": FEATURES,
        "label_type": "carrera_declarada_agrupada", "label_mapping": MEMBERS,
        "ranking_multiplier": {GROUP: chosen},
    }, artifacts / "riasec_model_42_ranking_experimental.joblib")
    print(report)


if __name__ == "__main__":
    main()
