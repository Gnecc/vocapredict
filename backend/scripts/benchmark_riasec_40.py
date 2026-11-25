"""Compare 40-class RIASEC classifiers on the original test split."""

import argparse
from functools import partial
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.kernel_approximation import RBFSampler
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

from models.riasec import BACKEND_DIR, FEATURES, SPLIT_SEED
from scripts.compare_riasec import load_profiles, percent, results, split, train
from scripts.prepare_riasec_dataset import QUESTIONS


def fit(model, rows, features=FEATURES):
    return model.fit(rows.loc[:, features].to_numpy(), rows["career_code"].to_numpy())


def logistic(rows, degree, power):
    y = rows["career_code"]
    counts = y.value_counts()
    weights = (len(y) / (len(counts) * y.map(counts).to_numpy())) ** power
    model = make_pipeline(
        StandardScaler(), PolynomialFeatures(degree=degree, include_bias=False),
        LogisticRegression(max_iter=800),
    )
    return model.fit(rows.loc[:, FEATURES].to_numpy(), y.to_numpy(),
                     logisticregression__sample_weight=weights)


def fit_rbf(rows, gamma):
    return fit(make_pipeline(
        StandardScaler(),
        RBFSampler(gamma=gamma, n_components=256, random_state=SPLIT_SEED),
        LogisticRegression(max_iter=700),
    ), rows)


def families():
    return {
        "Logística con interacciones": {
            f"grado {degree}, peso {power:g}": partial(logistic, degree=degree, power=power)
            for degree in (1, 2, 3) for power in (0.0, 0.3, 0.6)
        },
        "Red neuronal MLP": {
            f"capas {layers}": lambda rows, layers=layers: fit(make_pipeline(
                StandardScaler(), MLPClassifier(hidden_layer_sizes=layers, max_iter=120,
                                                 random_state=SPLIT_SEED),
            ), rows)
            for layers in ((32,), (64, 32), (128, 64))
        },
        "Logística con características RBF": {
            f"gamma {gamma:g}": partial(fit_rbf, gamma=gamma) for gamma in (0.05, 0.15, 0.4)
        },
        "k-NN": {
            f"{k} vecinos": lambda rows, k=k: fit(make_pipeline(
                StandardScaler(), KNeighborsClassifier(n_neighbors=k, n_jobs=2),
            ), rows)
            for k in (25, 100, 250)
        },
        "Random Forest": {
            f"hoja mínima {leaf}": lambda rows, leaf=leaf: fit(RandomForestClassifier(
                n_estimators=100, min_samples_leaf=leaf, random_state=SPLIT_SEED, n_jobs=2,
            ), rows)
            for leaf in (10, 30, 80)
        },
        "Extra Trees": {
            f"hoja mínima {leaf}": lambda rows, leaf=leaf: fit(ExtraTreesClassifier(
                n_estimators=100, min_samples_leaf=leaf, random_state=SPLIT_SEED, n_jobs=2,
            ), rows)
            for leaf in (10, 30, 80)
        },
        "Boosting de histogramas": {
            f"{stages} iteraciones": lambda rows, stages=stages: fit(HistGradientBoostingClassifier(
                max_iter=stages, max_leaf_nodes=15, l2_regularization=1,
                learning_rate=0.08, early_stopping=False, random_state=SPLIT_SEED,
            ), rows)
            for stages in (35, 60)
        },
        "Naive Bayes gaussiano": {
            f"suavizado {strength:g}": lambda rows, strength=strength: fit(
                GaussianNB(var_smoothing=strength), rows,
            )
            for strength in (0.001, 0.1)
        },
        "Discriminante cuadrático": {
            f"regularización {strength:g}": lambda rows, strength=strength: fit(
                QuadraticDiscriminantAnalysis(reg_param=strength), rows,
            )
            for strength in (0.01, 0.1, 0.4)
        },
    }


def evaluar(model, prueba, entrenamiento, features=FEATURES):
    if features == FEATURES:
        hits = results(model, prueba, entrenamiento)
    else:
        labels = prueba["career_code"].to_numpy()
        scores = model.predict_proba(prueba.loc[:, features].to_numpy())
        ranked = model.classes_[np.argsort(-scores, axis=1, kind="stable")[:, :3]]
        hits = pd.DataFrame({"career": labels, "top1": ranked[:, 0] == labels,
                             "top3": (ranked == labels[:, None]).any(axis=1)})
    by_class = hits.groupby("career")[["top1", "top3"]].mean()
    return (float(hits.top1.mean()), float(hits.top3.mean()),
            float(by_class.top1.mean()), float(by_class.top3.mean()))


def respuestas_originales(path, universo):
    raw = pd.read_csv(path, sep="\t", usecols=QUESTIONS)
    raw.index += 2  # source_row_id counts from the header of the original file.
    items = raw.reindex(universo.index).loc[:, QUESTIONS]
    values = items.to_numpy(dtype=float)
    reconstructed = values.reshape(-1, 6, 8).mean(axis=2) / 5
    if not np.isin(values, [1, 2, 3, 4, 5]).all() or not np.allclose(
        reconstructed, universo.loc[:, FEATURES].to_numpy(), rtol=0, atol=1e-6,
    ):
        raise ValueError("Las respuestas originales no corresponden a los seis puntajes.")
    return items


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--raw-riasec", type=Path, help="Archivo TSV original para probar las 48 respuestas.")
    args = parser.parse_args()
    universo = load_profiles(args.baseline)
    if universo["career_code"].nunique() != 40:
        parser.error("Se requiere el CSV histórico con 40 clases elegibles.")
    entrenamiento, prueba = split(universo)
    ajuste, validacion = split(entrenamiento)
    if set(entrenamiento.index) & set(prueba.index):
        raise ValueError("Entrenamiento y prueba comparten identificadores de origen.")
    groups = universo.groupby(list(FEATURES))["career_code"].agg(["size", "nunique"])
    conflicts = groups.loc[groups["nunique"].gt(1)]
    repeated = pd.MultiIndex.from_frame(prueba.loc[:, FEATURES]).isin(
        pd.MultiIndex.from_frame(entrenamiento.loc[:, FEATURES]),
    ).sum()
    frequent = entrenamiento["career_code"].value_counts()
    popular3 = prueba["career_code"].isin(frequent.index[:3]).mean()
    baselines = {"Clase más frecuente": lambda rows: fit(DummyClassifier(strategy="most_frequent"), rows),
                 "Regresión logística activa": train}
    evaluados = [(name, "fija", evaluar(spec(entrenamiento), prueba, entrenamiento))
                 for name, spec in baselines.items()]
    seleccion = []
    for familia, configuraciones in families().items():
        metrics = {}
        for etiqueta, spec in configuraciones.items():
            metrics[etiqueta] = evaluar(spec(ajuste), validacion, ajuste)
        ganadora = max(metrics, key=lambda n: metrics[n])
        seleccion.extend((familia, name, *values, name == ganadora) for name, values in metrics.items())
        score = evaluar(configuraciones[ganadora](entrenamiento), prueba, entrenamiento)
        evaluados.append((familia, ganadora, score))
        print(f"{familia}: {ganadora}, exactitud en prueba {percent(score[0])}", flush=True)

    item_scores = []
    if args.raw_riasec:
        items = respuestas_originales(args.raw_riasec, universo)
        for name, model in (
            ("Logística regularizada", make_pipeline(StandardScaler(), LogisticRegression(max_iter=600))),
            ("Red neuronal MLP", make_pipeline(StandardScaler(), MLPClassifier(
                hidden_layer_sizes=(64, 32), max_iter=120, random_state=SPLIT_SEED,
            ))),
        ):
            fit(model, entrenamiento.join(items), QUESTIONS)
            score = evaluar(model, prueba.join(items), entrenamiento, QUESTIONS)
            item_scores.append((name, score))
            print(f"48 respuestas · {name}: {percent(score[0])}", flush=True)

    lines = [
        "# Benchmark RIASEC de 40 carreras", "",
        f"Se reutilizaron los {len(prueba):,} casos de prueba originales.",
        f"Las configuraciones se eligieron por exactitud en {len(validacion):,} casos",
        "reservados del entrenamiento. En empate se usaron top 3 y exactitud equilibrada,",
        "en ese orden. Los modelos usan los seis puntajes RIASEC. La carrera declarada",
        "es el objetivo. El resultado es exploratorio porque la partición ya se conocía.", "",
        f"Las tres clases más frecuentes del entrenamiento obtienen {percent(popular3)} en top 3.",
        f"Hay {len(conflicts)} vectores de puntajes con etiquetas distintas ({conflicts['size'].sum()} filas).",
        f"{repeated} casos de prueba tienen un vector idéntico a alguno de entrenamiento.",
        "Estas coincidencias no establecen un techo de exactitud en perfiles nuevos.", "",
        "La MLP usa un presupuesto fijo de entrenamiento de hasta 120 iteraciones.",
        "",
        "| Modelo | Configuración | Primera opción | Top 3 | Exactitud equilibrada | Top 3 por clase |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for nombre, config, (top1, top3, balance, macro3) in evaluados:
        # A constant classifier only emits one option. The other classes are tied at zero.
        top3_text = "—" if nombre == "Clase más frecuente" else percent(top3)
        macro_text = "—" if nombre == "Clase más frecuente" else percent(macro3)
        lines.append(f"| {nombre} | {config} | {percent(top1)} | {top3_text} | "
                     f"{percent(balance)} | {macro_text} |")
    if item_scores:
        lines += [
            "", "## Las 48 respuestas como entrada", "",
            "Los modelos de esta sección usan las mismas preguntas antes de promediarlas.",
            "Se verificó la correspondencia con los seis puntajes de cada fila y se usó la",
            "misma partición. Las configuraciones se fijaron antes de consultar la prueba.",
            "", "| Modelo | Primera opción | Top 3 | Exactitud equilibrada |",
            "|---|---:|---:|---:|",
        ]
        for name, (top1, top3, balance, _) in item_scores:
            lines.append(f"| {name} | {percent(top1)} | {percent(top3)} | {percent(balance)} |")
    lines += [
        "", "## Selección dentro del entrenamiento", "",
        "| Familia | Configuración | Primera opción | Top 3 | Exactitud equilibrada | Elegida |",
        "|---|---|---:|---:|---:|---|",
    ]
    for familia, nombre, top1, top3, balance, _, elegido in seleccion:
        lines.append(f"| {familia} | {nombre} | {percent(top1)} | {percent(top3)} | "
                     f"{percent(balance)} | {'Sí' if elegido else '—'} |")
    lines += [
        "", "Desde `backend/`, con el CSV histórico de 40 carreras:", "",
        "```bash",
        "python3 -m scripts.benchmark_riasec_40 --baseline /ruta/al/csv-historico.csv --raw-riasec /ruta/al/data.csv",
        "```",
    ]
    report = BACKEND_DIR / "docs" / "benchmark_riasec_40.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
