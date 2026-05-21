from pathlib import Path

from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

from models.training_utils import load_labeled_dataset, save_artifact, save_metrics


def run(dataset_path: str | Path):
    path, _, X, y, encoder = load_labeled_dataset(dataset_path)
    model = KMeans(
        n_clusters=len(encoder.classes_),
        n_init=20,
        random_state=20260520,
    )
    clusters = model.fit_predict(X)
    metrics = {
        "dataset": str(path),
        "classes": encoder.classes_.tolist(),
        "adjusted_rand_score": float(adjusted_rand_score(y, clusters)),
        "inertia": float(model.inertia_),
    }

    save_artifact("kmeans_model.joblib", model)
    save_artifact("kmeans_label_encoder.joblib", encoder)
    save_metrics("kmeans", metrics)
    return metrics


if __name__ == "__main__":
    run("conjunto_de_datos_reetiquetados.xlsx")
