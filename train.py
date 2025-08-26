# train.py
import argparse
from models.factory import load_model_module

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=["svm","knn","rf","kmeans","fcm","pca"], default="svm")
    args = parser.parse_args()

    mod = load_model_module(args.model)

    # Preferimos una API común: run()
    if hasattr(mod, "run"):
        result = mod.run()
        if isinstance(result, dict) and result.get("auc_ovr") is not None:
            print(f"[train] {args.model} -> AUC(OvR) reportado: {result['auc_ovr']:.4f}")
    else:
        print(f"El módulo '{args.model}' no expone run(); quizá se ejecuta al importarlo.")

if __name__ == "__main__":
    main()
