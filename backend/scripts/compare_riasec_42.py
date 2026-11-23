"""Compare RIASEC models on the same holdout after grouping two labels."""

import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from models.riasec import BACKEND_DIR, DATASET, FEATURES
from scripts.check_riasec_journalism import fit_weighted
from scripts.compare_riasec import percent, train
from scripts.compare_riasec_43 import comparison_split_43


GROUP = "CPE"
GROUP_NAME = "Comunicación y Periodismo"
MEMBERS = {"COM": GROUP, "JOU": GROUP}
JOURNALISM_WEIGHT_43 = 1.3  # Seleccionado en el experimento de Periodismo.


def evaluate(model, test, combine="max"):
    raw = model.predict_proba(test.loc[:, FEATURES].to_numpy())
    return evaluate_scores(raw, model.classes_, test, combine=combine)


def evaluate_scores(raw, model_classes, test, combine="max", group_multiplier=1.0):
    mapped = np.array([MEMBERS.get(code, code) for code in model_classes])
    classes = np.unique(mapped)
    reduce_scores = np.max if combine == "max" else np.sum
    scores = np.column_stack([
        reduce_scores(raw[:, mapped == code], axis=1) for code in classes
    ])
    scores[:, classes == GROUP] *= group_multiplier
    ranked = classes[np.argsort(-scores, axis=1, kind="stable")[:, :3]]
    source = test["career_code"]
    target = source.replace(MEMBERS).to_numpy()
    return pd.DataFrame({
        "source": source,
        "target": target,
        "top1": ranked[:, 0] == target,
        "top3": (ranked == target[:, None]).any(axis=1),
        "shows_group": (ranked == GROUP).any(axis=1),
    }, index=test.index)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, default=DATASET)
    args = parser.parse_args()

    train40, train43, shared, new = comparison_split_43(args.baseline, args.dataset)
    train42 = train43.assign(career_code=train43["career_code"].replace(MEMBERS))
    test = pd.concat([shared, new], verify_integrity=True)
    if train42["career_code"].nunique() != 42 or not train42.index.equals(train43.index):
        raise ValueError("Se esperaban 42 clases con los mismos perfiles de entrenamiento del modelo de 43.")
    model40, model43, model42 = train(train40), train(train43), train(train42)
    evaluations = {
        "40 original": evaluate(model40, test), "43 original": evaluate(model43, test),
        "43 ajustado": evaluate(fit_weighted(train43, JOURNALISM_WEIGHT_43), test),
        "42 agrupado": evaluate(model42, test),
        "43 con suma al mostrar": evaluate(model43, test, combine="sum"),
    }
    names = train43.set_index("career_code")["career_name"].to_dict()
    for code in MEMBERS:
        del names[code]
    names[GROUP] = GROUP_NAME

    lines = [
        "# RIASEC de 42 clases con Comunicación y Periodismo agrupadas", "",
        f"El entrenamiento de 42 clases reutiliza los {len(train43):,} perfiles del modelo de 43.",
        f"Agrupa {train43.career_code.eq('COM').sum()} casos de Comunicación y "
        f"{train43.career_code.eq('JOU').sum()} de Periodismo. Se conserva la regresión logística",
        "y se recalculan los pesos por frecuencia de las 42 clases.",
        f"La prueba usa los mismos {len(shared):,} casos compartidos y {len(new):,} nuevos.",
        "Se conservan las etiquetas originales para desglosar resultados y se usa la etiqueta",
        "agrupada como objetivo común. Para los modelos anteriores se asigna al grupo",
        "la mayor puntuación de sus integrantes antes de ordenar las tres opciones distintas.",
        "El modelo de 40 solo aporta Periodismo al grupo. También se prueba sumar las dos",
        "puntuaciones del modelo de 43 antes de ordenar. Son puntuaciones relativas.",
        f"El de 43 ajustado usa el multiplicador histórico de Periodismo de {JOURNALISM_WEIGHT_43:g}×.",
        "La partición se usó en estudios previos. Estos resultados son exploratorios.", "",
        "| Modelo | Grupo de prueba | Casos | Top 1 | Top 3 | Top 3 promedio por clase |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for name, hits in evaluations.items():
        groups = (
            ("Compartidos", hits.loc[shared.index]),
            ("Nuevos", hits.loc[new.index]),
            ("Todos", hits),
            ("Fuera de Comunicación y Periodismo", hits.loc[~hits.target.eq(GROUP)]),
        )
        for label, group in groups:
            macro = group.groupby("target")["top3"].mean().mean()
            lines.append(f"| {name} | {label} | {len(group):,} | {percent(group.top1.mean())} | "
                         f"{percent(group.top3.mean())} | {percent(macro)} |")

    lines += [
        "", "## Aciertos del grupo en el top 3", "",
        "| Modelo | Periodismo original | Comunicación original | Total del grupo | Precisión del grupo |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, hits in evaluations.items():
        jou = hits.loc[hits.source.eq("JOU"), "top3"]
        com = hits.loc[hits.source.eq("COM"), "top3"]
        correct = jou.sum() + com.sum()
        suggested = hits.shows_group.sum()
        precision = f"{correct}/{suggested} ({percent(correct / suggested)})" if suggested else "—"
        lines.append(f"| {name} | {jou.sum()}/{len(jou)} | {com.sum()}/{len(com)} | "
                     f"{correct}/{len(jou) + len(com)} | {precision} |")

    lines += [
        "", "## Top 3 por clase agrupada", "",
        "Los conteos muestran aciertos sobre el total de casos de prueba de cada clase.", "",
        "| Clase | " + " | ".join(evaluations) + " |",
        "|---|" + "---:|" * len(evaluations),
    ]
    per_model = {name: hits.groupby("target")["top3"].agg(["sum", "size"])
                 for name, hits in evaluations.items()}
    for code in sorted(names, key=names.get):
        cells = [f"{metrics.loc[code, 'sum']}/{metrics.loc[code, 'size']}" for metrics in per_model.values()]
        lines.append(f"| {names[code]} | " + " | ".join(cells) + " |")

    lines += [
        "", "Para reproducir desde `backend/` con el CSV histórico de las 40 clases:", "",
        "```bash",
        "python3 -m scripts.compare_riasec_42 --baseline /ruta/al/csv-historico.csv",
        "```",
    ]
    report = BACKEND_DIR / "docs" / "comparacion_riasec_40_42_43.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    artifacts = BACKEND_DIR / "artifacts"
    artifacts.mkdir(exist_ok=True)
    joblib.dump({
        "model": model42, "career_labels": names, "features": FEATURES,
        "label_type": "carrera_declarada_agrupada", "label_mapping": MEMBERS,
    }, artifacts / "riasec_model_42.joblib")
    print(report)


if __name__ == "__main__":
    main()
