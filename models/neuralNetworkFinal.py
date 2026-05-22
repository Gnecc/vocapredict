from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_DATASET = Path("conjunto_de_datos_reetiquetados.xlsx")
ARTIFACTS_DIR = Path("artifacts")
RANDOM_SEED = 20260520


class NeuralNetwork:
    def __init__(
        self,
        input_size: int,
        hidden_sizes: tuple[int, int],
        output_size: int,
        learning_rate: float = 0.01,
        l2: float = 0.0005,
        seed: int = RANDOM_SEED,
    ):
        rng = np.random.default_rng(seed)
        hidden_1, hidden_2 = hidden_sizes
        self.learning_rate = learning_rate
        self.l2 = l2
        self.weights = [
            rng.normal(0, np.sqrt(2 / input_size), size=(input_size, hidden_1)),
            rng.normal(0, np.sqrt(2 / hidden_1), size=(hidden_1, hidden_2)),
            rng.normal(0, np.sqrt(2 / hidden_2), size=(hidden_2, output_size)),
        ]
        self.biases = [
            np.zeros((1, hidden_1)),
            np.zeros((1, hidden_2)),
            np.zeros((1, output_size)),
        ]

    @staticmethod
    def relu(values: np.ndarray) -> np.ndarray:
        return np.maximum(values, 0)

    @staticmethod
    def relu_gradient(values: np.ndarray) -> np.ndarray:
        return (values > 0).astype(float)

    @staticmethod
    def softmax(values: np.ndarray) -> np.ndarray:
        shifted = values - np.max(values, axis=1, keepdims=True)
        exp_values = np.exp(shifted)
        return exp_values / np.sum(exp_values, axis=1, keepdims=True)

    def forward(self, X: np.ndarray):
        z1 = X @ self.weights[0] + self.biases[0]
        a1 = self.relu(z1)
        z2 = a1 @ self.weights[1] + self.biases[1]
        a2 = self.relu(z2)
        logits = a2 @ self.weights[2] + self.biases[2]
        probabilities = self.softmax(logits)
        return z1, a1, z2, a2, probabilities

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.forward(X)[-1]

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.argmax(self.predict_proba(X), axis=1)

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epochs: int = 1200,
        batch_size: int = 32,
    ):
        rng = np.random.default_rng(RANDOM_SEED)
        class_count = self.biases[-1].shape[1]

        for _ in range(epochs):
            order = rng.permutation(len(X))
            for start in range(0, len(X), batch_size):
                batch_index = order[start : start + batch_size]
                X_batch = X[batch_index]
                y_batch = y[batch_index]
                z1, a1, z2, a2, probabilities = self.forward(X_batch)

                expected = np.eye(class_count)[y_batch]
                batch_len = len(X_batch)
                delta3 = (probabilities - expected) / batch_len
                delta2 = (delta3 @ self.weights[2].T) * self.relu_gradient(z2)
                delta1 = (delta2 @ self.weights[1].T) * self.relu_gradient(z1)

                gradients_w = [
                    X_batch.T @ delta1 + self.l2 * self.weights[0],
                    a1.T @ delta2 + self.l2 * self.weights[1],
                    a2.T @ delta3 + self.l2 * self.weights[2],
                ]
                gradients_b = [
                    np.sum(delta1, axis=0, keepdims=True),
                    np.sum(delta2, axis=0, keepdims=True),
                    np.sum(delta3, axis=0, keepdims=True),
                ]

                for index in range(len(self.weights)):
                    self.weights[index] -= self.learning_rate * gradients_w[index]
                    self.biases[index] -= self.learning_rate * gradients_b[index]


def load_dataset(dataset_path: str | Path):
    path = Path(dataset_path)
    if path.suffix.lower() == ".csv":
        dataframe = pd.read_csv(path)
    else:
        dataframe = pd.read_excel(path)

    features = dataframe.iloc[:, :-1].to_numpy(dtype=float)
    labels = dataframe.iloc[:, -1].astype(str).str.strip().to_numpy()
    classes = np.array(sorted(set(labels)))
    class_index = {label: index for index, label in enumerate(classes)}
    encoded_labels = np.array([class_index[label] for label in labels], dtype=int)
    return path, features, encoded_labels, classes


def stratified_split(
    X: np.ndarray,
    y: np.ndarray,
    test_size: float = 0.25,
):
    rng = np.random.default_rng(RANDOM_SEED)
    train_index = []
    test_index = []

    for label in np.unique(y):
        label_index = np.flatnonzero(y == label)
        rng.shuffle(label_index)
        label_test_rows = max(1, int(round(len(label_index) * test_size)))
        test_index.extend(label_index[:label_test_rows])
        train_index.extend(label_index[label_test_rows:])

    train_index = rng.permutation(train_index)
    test_index = rng.permutation(test_index)
    return X[train_index], X[test_index], y[train_index], y[test_index]


def standardize_train_test(X_train: np.ndarray, X_test: np.ndarray):
    mean = np.mean(X_train, axis=0)
    scale = np.std(X_train, axis=0)
    scale[scale == 0] = 1
    return (X_train - mean) / scale, (X_test - mean) / scale, mean, scale


def accuracy(predictions: np.ndarray, expected: np.ndarray) -> float:
    return float(np.mean(predictions == expected))


def save_artifacts(
    network: NeuralNetwork,
    classes: np.ndarray,
    mean: np.ndarray,
    scale: np.ndarray,
    metrics: dict,
):
    ARTIFACTS_DIR.mkdir(exist_ok=True)
    np.savez(
        ARTIFACTS_DIR / "neural_network_model.npz",
        weight_1=network.weights[0],
        weight_2=network.weights[1],
        weight_3=network.weights[2],
        bias_1=network.biases[0],
        bias_2=network.biases[1],
        bias_3=network.biases[2],
        mean=mean,
        scale=scale,
    )
    (ARTIFACTS_DIR / "neural_network_labels.json").write_text(
        json.dumps(classes.tolist(), indent=2, ensure_ascii=True) + "\n"
    )
    (ARTIFACTS_DIR / "neural_network_metrics.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=True) + "\n"
    )


def run(dataset_path: str | Path = DEFAULT_DATASET):
    path, X, y, classes = load_dataset(dataset_path)
    X_train, X_test, y_train, y_test = stratified_split(X, y)
    X_train, X_test, mean, scale = standardize_train_test(X_train, X_test)

    network = NeuralNetwork(
        input_size=X_train.shape[1],
        hidden_sizes=(32, 16),
        output_size=len(classes),
    )
    network.fit(X_train, y_train)
    metrics = {
        "accuracy": accuracy(network.predict(X_test), y_test),
        "dataset": str(path),
        "classes": classes.tolist(),
        "train_rows": int(len(y_train)),
        "test_rows": int(len(y_test)),
        "implementation": "numpy",
    }
    save_artifacts(network, classes, mean, scale, metrics)
    return metrics


if __name__ == "__main__":
    run()
