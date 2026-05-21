from pathlib import Path

from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from models.training_utils import load_labeled_dataset, save_artifact, save_metrics


def run(dataset_path: str | Path):
    path, dataframe, X, _, _ = load_labeled_dataset(dataset_path)
    model = make_pipeline(StandardScaler(), PCA())
    model.fit(X)
    pca = model.named_steps["pca"]
    metrics = {
        "dataset": str(path),
        "features": dataframe.columns[:-1].tolist(),
        "explained_variance_ratio": [
            float(value) for value in pca.explained_variance_ratio_
        ],
        "cumulative_explained_variance": [
            float(value) for value in pca.explained_variance_ratio_.cumsum()
        ],
    }

    save_artifact("pca_pipeline.joblib", model)
    save_metrics("pca", metrics)
    return metrics


if __name__ == "__main__":
    run("conjunto_de_datos_reetiquetados.xlsx")
