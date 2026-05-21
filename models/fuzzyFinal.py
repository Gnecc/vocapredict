from pathlib import Path

import numpy as np
from sklearn.metrics import adjusted_rand_score

from models.training_utils import load_labeled_dataset, save_artifact, save_metrics


def fuzzy_c_means(
    values: np.ndarray,
    n_clusters: int,
    fuzziness: float = 2.0,
    max_iter: int = 300,
    tolerance: float = 1e-6,
    random_seed: int = 20260520,
):
    rng = np.random.default_rng(random_seed)
    membership = rng.random((len(values), n_clusters))
    membership = membership / membership.sum(axis=1, keepdims=True)

    for _ in range(max_iter):
        weighted = membership**fuzziness
        centers = (weighted.T @ values) / weighted.sum(axis=0)[:, None]
        distances = np.linalg.norm(values[:, None, :] - centers[None, :, :], axis=2)
        distances = np.maximum(distances, 1e-12)
        ratio = distances[:, :, None] / distances[:, None, :]
        updated = 1 / np.sum(ratio ** (2 / (fuzziness - 1)), axis=2)
        if np.max(np.abs(updated - membership)) < tolerance:
            membership = updated
            break
        membership = updated

    return centers, membership


def run(dataset_path: str | Path):
    path, _, X, y, encoder = load_labeled_dataset(dataset_path)
    values = X.to_numpy(dtype=float)
    centers, membership = fuzzy_c_means(values, len(encoder.classes_))
    clusters = membership.argmax(axis=1)
    metrics = {
        "dataset": str(path),
        "classes": encoder.classes_.tolist(),
        "adjusted_rand_score": float(adjusted_rand_score(y, clusters)),
        "fuzzy_partition_coefficient": float(np.mean(np.sum(membership**2, axis=1))),
    }

    save_artifact(
        "fuzzy_c_means_model.joblib",
        {"centers": centers, "membership": membership, "classes": encoder.classes_},
    )
    save_metrics("fuzzy_c_means", metrics)
    return metrics


if __name__ == "__main__":
    run("conjunto_de_datos_reetiquetados.xlsx")
