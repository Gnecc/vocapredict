from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


DEFAULT_DATASET = Path("conjunto_de_datos_reetiquetados.xlsx")
ARTIFACTS_DIR = Path("artifacts")


def load_labeled_dataset(dataset_path: str | Path = DEFAULT_DATASET):
    path = Path(dataset_path)
    if path.suffix.lower() == ".csv":
        dataframe = pd.read_csv(path)
    else:
        dataframe = pd.read_excel(path)

    features = dataframe.iloc[:, :-1].astype(float)
    labels = dataframe.iloc[:, -1].astype(str).str.strip()
    encoder = LabelEncoder().fit(labels)
    encoded_labels = encoder.transform(labels)
    return path, dataframe, features, encoded_labels, encoder


def split_labeled_dataset(features, labels, test_size: float = 0.25):
    values = features.to_numpy(dtype=float)
    return train_test_split(
        values,
        labels,
        test_size=test_size,
        random_state=20260520,
        stratify=labels,
    )


def augment_training_split(X_train, y_train, random_seed: int = 20260520):
    rng = np.random.default_rng(random_seed)
    target_per_class = len(y_train)
    rows = [X_train]
    labels = [y_train]

    for label in np.unique(y_train):
        class_values = X_train[y_train == label]
        distances = np.linalg.norm(
            class_values[:, None, :] - class_values[None, :, :],
            axis=2,
        )
        np.fill_diagonal(distances, np.inf)
        neighbor_order = np.argsort(distances, axis=1)
        neighbor_limit = min(5, len(class_values) - 1)
        requested = target_per_class - len(class_values)
        synthetic = []

        for _ in range(requested):
            seed_pos = int(rng.integers(0, len(class_values)))
            neighbor_pos = int(rng.choice(neighbor_order[seed_pos, :neighbor_limit]))
            alpha = float(rng.random())
            synthetic.append(
                class_values[seed_pos]
                + alpha * (class_values[neighbor_pos] - class_values[seed_pos])
            )

        rows.append(np.array(synthetic, dtype=float))
        labels.append(np.full(requested, label, dtype=y_train.dtype))

    augmented_X = np.vstack(rows)
    augmented_y = np.concatenate(labels)
    order = rng.permutation(len(augmented_y))
    metadata = {
        "train_real_rows": int(len(y_train)),
        "train_synthetic_rows": int(len(augmented_y) - len(y_train)),
        "train_augmented_rows": int(len(augmented_y)),
        "train_synthetic_ratio": float((len(augmented_y) - len(y_train)) / len(augmented_y)),
        "train_target_per_class": int(target_per_class),
    }
    return augmented_X[order], augmented_y[order], metadata


def prepare_supervised_training(dataset_path: str | Path = DEFAULT_DATASET):
    path, dataframe, features, labels, encoder = load_labeled_dataset(dataset_path)
    X_train, X_test, y_train, y_test = split_labeled_dataset(features, labels)
    X_augmented, y_augmented, metadata = augment_training_split(X_train, y_train)
    metadata["test_real_rows"] = int(len(y_test))
    metadata["evaluation_dataset"] = "real holdout split before augmentation"
    return path, dataframe, X_augmented, X_test, y_augmented, y_test, encoder, metadata


def classifier_report(model, X_test, y_test, encoder: LabelEncoder) -> dict:
    predictions = model.predict(X_test)
    report = classification_report(
        y_test,
        predictions,
        labels=list(range(len(encoder.classes_))),
        target_names=encoder.classes_,
        output_dict=True,
        zero_division=0,
    )
    return {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "classification_report": report,
    }


def save_artifact(name: str, value) -> Path:
    ARTIFACTS_DIR.mkdir(exist_ok=True)
    path = ARTIFACTS_DIR / name
    joblib.dump(value, path)
    return path


def save_metrics(model_name: str, metrics: dict) -> Path:
    ARTIFACTS_DIR.mkdir(exist_ok=True)
    path = ARTIFACTS_DIR / f"{model_name}_metrics.json"
    path.write_text(json.dumps(metrics, indent=2, ensure_ascii=True) + "\n")
    return path
