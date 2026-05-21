from pathlib import Path

from sklearn.ensemble import RandomForestClassifier

from models.training_utils import (
    classifier_report,
    prepare_supervised_training,
    save_artifact,
    save_metrics,
)


def run(dataset_path: str | Path):
    path, dataframe, X_train, X_test, y_train, y_test, encoder, split_meta = (
        prepare_supervised_training(dataset_path)
    )

    classifier = RandomForestClassifier(
        n_estimators=200,
        criterion="entropy",
        random_state=20260520,
    )
    classifier.fit(X_train, y_train)
    metrics = classifier_report(classifier, X_test, y_test, encoder)
    metrics["dataset"] = str(path)
    metrics["classes"] = encoder.classes_.tolist()
    metrics.update(split_meta)
    metrics["feature_importances"] = {
        name: float(value)
        for name, value in zip(dataframe.columns[:-1], classifier.feature_importances_)
    }

    save_artifact("random_forest_model.joblib", classifier)
    save_artifact("random_forest_label_encoder.joblib", encoder)
    save_metrics("random_forest", metrics)
    return metrics


if __name__ == "__main__":
    run("conjunto_de_datos_reetiquetados.xlsx")
