from importlib import import_module

SUPPORTED = {
    "svm": "models.svmFinal",
    "knn": "models.knnFinal",
    "rf":  "models.randomForestFinal",
    "nn": "models.neuralNetworkFinal",
    "kmeans": "models.kmeansFinal",
    "fcm": "models.fuzzyFinal",
    "pca": "models.PCAFinal",
}

def load_model_module(name: str):
    if name not in SUPPORTED:
        raise ValueError(f"Modelo no soportado: {name}")
    return import_module(SUPPORTED[name])
