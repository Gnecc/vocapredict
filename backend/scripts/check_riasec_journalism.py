"""Measure the effect of Communication and test extra weight for Journalism."""

import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold

from models.riasec import BACKEND_DIR, DATASET, FEATURES, SPLIT_SEED, fit_classifier
from scripts.compare_riasec import percent, results, train
from scripts.compare_riasec_43 import comparison_split_43


FACTORS = (1.0, 1.15, 1.3, 1.5, 1.75, 2.0, 2.5, 3.0)
SHARED_LOSS = 0.01
COMMUNICATION_LOSS = 0.03


def fit_weighted(rows, factor):
    return fit_classifier(
        rows.loc[:, FEATURES].to_numpy(), rows["career_code"].to_numpy(), {"JOU": factor},
    )


def scores(hits, shared):
    journalism = hits.loc[hits.career.eq("JOU"), "top3"].mean()
    communication = hits.loc[hits.career.eq("COM"), "top3"].mean()
    common = hits.loc[hits.career.isin(shared), "top3"].mean()
    return journalism, communication, common


def ranked(model, profiles, without=None):
    predictions = model.predict_proba(profiles.loc[:, FEATURES].to_numpy())
    if without is not None:
        predictions[:, model.classes_ == without] = -np.inf
    return model.classes_[np.argsort(-predictions, axis=1, kind="stable")[:, :3]]


def top3_count(rankings, code):
    return int(np.any(rankings == code, axis=1).sum())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, default=DATASET)
    args = parser.parse_args()

    train40, train43, shared_test, new_test = comparison_split_43(args.baseline, args.dataset)
    common_codes = set(train40["career_code"])
    test = pd.concat([shared_test, new_test], verify_integrity=True)
    journalism_test = shared_test.loc[shared_test.career_code.eq("JOU")]

    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=SPLIT_SEED)
    folds = list(cv.split(train43, train43["career_code"]))
    validation = {}
    for factor in FACTORS:
        predictions = []
        for fit_indices, val_indices in folds:
            fit_rows = train43.iloc[fit_indices]
            val_rows = train43.iloc[val_indices]
            predictions.append(results(fit_weighted(fit_rows, factor), val_rows, fit_rows))
        validation[factor] = scores(pd.concat(predictions), common_codes)

    _, baseline_com, baseline_common = validation[1.0]
    feasible = [
        factor for factor, (_, com, common) in validation.items()
        if com >= baseline_com - COMMUNICATION_LOSS and common >= baseline_common - SHARED_LOSS
    ]
    chosen = max(feasible, key=lambda factor: (validation[factor][0], -factor))
    model40, model43 = train(train40), train(train43)
    adjusted = fit_weighted(train43, chosen)
    without_com = train(train43.loc[~train43.career_code.eq("COM")])

    ranking40 = ranked(model40, journalism_test)
    ranking43 = ranked(model43, journalism_test)
    baseline_hits = np.any(ranking40 == "JOU", axis=1)
    lost = baseline_hits & ~np.any(ranking43 == "JOU", axis=1)
    hidden = ranked(model43, journalism_test, without="COM")
    ablation = ranked(without_com, journalism_test)
    count = len(journalism_test)
    lines = [
        "# Periodismo y Comunicación en el predictor RIASEC", "",
        f"Se reutilizaron los {len(shared_test):,} casos compartidos y los {len(new_test):,} nuevos",
        f"del experimento 40 vs. 43. Entre los {count} casos declarados de Periodismo,",
        f"Comunicación apareció en el top 3 del modelo de 43 en {top3_count(ranking43, 'COM')}.",
        f"Apareció en {top3_count(ranking43[lost], 'COM')} de los {lost.sum()} casos que",
        "el modelo de 40 acertaba y el de 43 dejó de acertar.", "",
        "| Diagnóstico sobre Periodismo | Aciertos top 3 |",
        "|---|---:|",
        f"| Modelo de 40 | {top3_count(ranking40, 'JOU')}/{count} |",
        f"| Modelo de 43 | {top3_count(ranking43, 'JOU')}/{count} |",
        f"| Modelo de 43 ocultando Comunicación al ordenar | {top3_count(hidden, 'JOU')}/{count} |",
        f"| Reentrenamiento de 42 sin Comunicación | {top3_count(ablation, 'JOU')}/{count} |",
        "", "## Ajuste de peso", "",
        "Se escogió el multiplicador con más aciertos en Periodismo en tres pliegues",
        "estratificados dentro del entrenamiento. Se permitió perder hasta un punto",
        "porcentual en las carreras compartidas y hasta tres en Comunicación frente",
        "al de 43 sin ajuste, medidos durante la validación interna. Los empates",
        "favorecen el multiplicador menor. La partición de prueba ya era conocida de",
        "experimentos anteriores, por lo que los resultados son exploratorios.", "",
        "| Peso de Periodismo | Top 3 Periodismo | Top 3 Comunicación | Top 3 compartidas | Cumple límites |",
        "|---:|---:|---:|---:|---|",
    ]
    for factor, row in validation.items():
        metrics = " | ".join(map(percent, row))
        lines.append(f"| {factor:g} | {metrics} | {'Sí' if factor in feasible else 'No'} |")
    lines += [
        "", f"Multiplicador elegido sobre el peso original de Periodismo **{chosen:g}×**.",
        "", "## Evaluación en la misma prueba", "",
        "La precisión de Periodismo es la proporción de recomendaciones en las que",
        "Periodismo aparece en el top 3 y coincide con la carrera declarada.", "",
        "| Modelo | Top 3 Periodismo | Precisión de Periodismo | Top 3 Comunicación | Top 3 compartidas | Top 3 nuevas | Top 3 total |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, model, training in (
        ("40 original", model40, train40), ("43 original", model43, train43),
        ("43 ajustado", adjusted, train43),
    ):
        hits = results(model, test, training)
        jou = hits.loc[hits.career.eq("JOU"), "top3"]
        com = hits.loc[hits.career.eq("COM"), "top3"]
        _, _, common = scores(hits, common_codes)
        new = hits.loc[new_test.index, "top3"].mean()
        jou_suggestions = top3_count(ranked(model, test), "JOU")
        precision = f"{jou.sum()}/{jou_suggestions}" if jou_suggestions else "—"
        com_count = f"{com.sum()}/{len(com)}" if "COM" in model.classes_ else "—"
        lines.append(f"| {name} | {jou.sum()}/{len(jou)} | {precision} | {com_count} | "
                     f"{percent(common)} | {percent(new)} | {percent(hits.top3.mean())} |")
    lines += [
        "", "Para reproducir desde `backend/` con el mismo CSV de las 40 clases:", "",
        "```bash",
        "python3 -m scripts.check_riasec_journalism --baseline /ruta/al/csv-historico.csv",
        "```",
    ]
    report = BACKEND_DIR / "docs" / "periodismo_comunicacion_riasec.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    artifacts = BACKEND_DIR / "artifacts"
    artifacts.mkdir(exist_ok=True)
    joblib.dump({
        "model": adjusted,
        "career_labels": train43.set_index("career_code")["career_name"].to_dict(),
        "features": FEATURES,
        "label_type": "carrera_declarada",
        "journalism_weight_multiplier": chosen,
    }, artifacts / "riasec_model_43_periodismo.joblib")
    print(report)


if __name__ == "__main__":
    main()
