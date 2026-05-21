from pathlib import Path

from sklearn.neighbors import KNeighborsClassifier

from models.training_utils import (
    classifier_report,
    prepare_supervised_training,
    save_artifact,
    save_metrics,
)


def run(dataset_path: str | Path):
    path, _, X_train, X_test, y_train, y_test, encoder, split_meta = (
        prepare_supervised_training(dataset_path)
    )

    classifier = KNeighborsClassifier(n_neighbors=5)
    classifier.fit(X_train, y_train)
    metrics = classifier_report(classifier, X_test, y_test, encoder)
    metrics["dataset"] = str(path)
    metrics["classes"] = encoder.classes_.tolist()
    metrics.update(split_meta)

    save_artifact("knn_model.joblib", classifier)
    save_artifact("knn_label_encoder.joblib", encoder)
    save_metrics("knn", metrics)
    return metrics


if __name__ == "__main__":
    run("conjunto_de_datos_reetiquetados.xlsx")
