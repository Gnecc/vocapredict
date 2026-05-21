from pathlib import Path

import joblib
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import SVC

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

    classifier = OneVsRestClassifier(
        SVC(kernel="linear", probability=True, random_state=20260520)
    )
    classifier.fit(X_train, y_train)
    metrics = classifier_report(classifier, X_test, y_test, encoder)
    metrics["dataset"] = str(path)
    metrics["classes"] = encoder.classes_.tolist()
    metrics.update(split_meta)

    joblib.dump(classifier, "svm_model.joblib")
    joblib.dump(encoder, "label_encoder.joblib")
    save_artifact("svm_model.joblib", classifier)
    save_artifact("svm_label_encoder.joblib", encoder)
    save_metrics("svm", metrics)
    return metrics


if __name__ == "__main__":
    run("conjunto_de_datos_reetiquetados.xlsx")
