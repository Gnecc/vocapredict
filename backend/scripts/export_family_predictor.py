"""Export the frozen Optuna family benchmark for the prediction API."""

import argparse
import warnings
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.kernel_approximation import RBFSampler
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline, make_union
from sklearn.preprocessing import FunctionTransformer, PolynomialFeatures, StandardScaler

from family_prediction import family_scores
from models.riasec import BACKEND_DIR, FEATURES, SPLIT_SEED
from scripts.benchmark_riasec_40 import respuestas_originales
from scripts.compare_riasec import load_profiles, split
from scripts.compare_riasec_families import FAMILY_BY_CODE


CLASSES = np.array(sorted(set(FAMILY_BY_CODE.values())))
# Frozen parameters selected by Optuna for top-3 accuracy.
OPTUNA_PARAMS = {
    "Logística con interacciones": {
        "entrada": "interacciones", "sesgo_frecuencia": 0.2221583348427519, "C": 0.20070355064727777,
    },
    "Red neuronal": {
        "entrada": "respuestas", "sesgo_frecuencia": -0.10312479729312918, "unidades": 32,
        "epocas": 50, "alpha": 0.9900785396423306, "tasa": 0.0027282154027970067,
    },
    "Boosting": {
        "entrada": "respuestas y áreas", "sesgo_frecuencia": 0.002999159146567121, "hojas": 5,
        "iteraciones": 120, "tasa": 0.11049765635138668, "l2": 12.769850191537678, "min_hoja": 70,
    },
}
BLEND_PARAMS = {"peso_0": 0.2130085285714835, "peso_1": 0.034901720874466184,
                "peso_2": 0.3418450128354894, "peso_3": 0.9656810978736545,
                "ajuste_frecuencia": 0.04711279049196397}

MODEL_NAMES = ("Logística con interacciones", "Red neuronal", "Boosting")


def model_inputs(items, areas):
    terms = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False).set_output(transform="pandas")
    return {"respuestas": items, "respuestas y áreas": items.join(areas),
            "interacciones": items.join(terms.fit_transform(areas))}


def train_candidate(name, params, inputs, training, label):
    values = inputs[params["entrada"]]
    if name == "Logística con interacciones":
        model = make_pipeline(StandardScaler(), LogisticRegression(C=params["C"], max_iter=600))
    elif name == "Red neuronal":
        model = make_pipeline(StandardScaler(), MLPClassifier(
            hidden_layer_sizes=(params["unidades"],), alpha=params["alpha"],
            learning_rate_init=params["tasa"], max_iter=params["epocas"], random_state=SPLIT_SEED,
        ))
    else:
        model = HistGradientBoostingClassifier(
            max_leaf_nodes=params["hojas"], max_iter=params["iteraciones"], learning_rate=params["tasa"],
            l2_regularization=params["l2"], min_samples_leaf=params["min_hoja"],
            early_stopping=False, random_state=SPLIT_SEED,
        )
    labels = label.loc[training.index]
    weights = (labels.map(labels.value_counts()).to_numpy(dtype=float)) ** params["sesgo_frecuencia"]
    weights /= weights.mean()
    weight_key = "sample_weight" if name == "Boosting" else f"{model.steps[-1][0]}__sample_weight"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        model.fit(values.loc[training.index], labels, **{weight_key: weights})
    return model


def fit_reference_model(training, items, power, grouped, *, nonlinear=False):
    families = training.career_code.map(FAMILY_BY_CODE)
    labels = training.career_code if grouped else families
    weights = families.map(families.value_counts()).to_numpy(dtype=float) ** -power
    steps = [StandardScaler()]
    if nonlinear:
        steps.append(make_union(FunctionTransformer(), RBFSampler(
            gamma=1 / 96, n_components=256, random_state=SPLIT_SEED,
        )))
    model = make_pipeline(*steps, LogisticRegression(max_iter=600))
    model.fit(items.loc[training.index], labels, logisticregression__sample_weight=weights / weights.mean())
    return model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--raw-riasec", type=Path, required=True)
    args = parser.parse_args()
    rows = load_profiles(args.baseline)
    training, test = split(rows)
    items = respuestas_originales(args.raw_riasec, rows)
    inputs = model_inputs(items, rows.loc[:, FEATURES])
    labels = rows.career_code.map(FAMILY_BY_CODE)
    direct = fit_reference_model(training, items, 0.25, False, nonlinear=True)
    grouped = fit_reference_model(training, items, 0, True)
    memberships = np.array([FAMILY_BY_CODE[code] for code in grouped.classes_])[:, None] == CLASSES
    priors = labels.loc[training.index].value_counts(normalize=True).reindex(CLASSES).to_numpy()
    candidates = [(OPTUNA_PARAMS[name]["entrada"], train_candidate(name, OPTUNA_PARAMS[name], inputs, training, labels))
                  for name in MODEL_NAMES]
    artifact = dict(questions=list(items.columns), areas=list(FEATURES), families=list(CLASSES),
                    direct=direct, grouped=grouped, memberships=memberships, candidates=candidates,
                    weights=[BLEND_PARAMS[f"peso_{i}"] for i in range(4)],
                    prior_factor=priors ** BLEND_PARAMS["ajuste_frecuencia"])
    ranked = CLASSES[np.argsort(-family_scores(artifact, items.loc[test.index].to_numpy()), axis=1, kind="stable")]
    correct = ranked == labels.loc[test.index].to_numpy()[:, None]
    hits = tuple(int(correct[:, :k].any(axis=1).sum()) for k in (3, 4))
    if hits != (6163, 6766) or len(test) != 8083:
        raise ValueError(f"No se reprodujo la prueba histórica: {hits} en {len(test)} perfiles.")
    joblib.dump(artifact, BACKEND_DIR / "riasec_families.joblib", compress=3)
    print(f"Aciertos top 3 y top 4: {hits} en {len(test)} perfiles.")


if __name__ == "__main__":
    main()
