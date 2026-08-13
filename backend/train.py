import argparse
import inspect
from models.factory import load_model_module

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=["svm","knn","rf","nn","kmeans","fcm","pca"], default="svm")
    parser.add_argument(
        "--dataset",
        default="data/conjunto_de_datos_aumentado_75_sintetico_amai.csv",
        help="Dataset CSV o XLSX usado para entrenar.",
    )
    parser.add_argument(
        "--augment-train",
        action="store_true",
        help="Aplica aumento sintetico adicional solo al split de entrenamiento.",
    )
    args = parser.parse_args()

    mod = load_model_module(args.model)

    if hasattr(mod, "run"):
        run_signature = inspect.signature(mod.run)
        if "augment_train" in run_signature.parameters:
            result = mod.run(args.dataset, augment_train=args.augment_train)
        else:
            result = mod.run(args.dataset)
        if isinstance(result, dict) and result.get("auc_ovr") is not None:
            print(f"[train] {args.model} -> AUC(OvR) reportado: {result['auc_ovr']:.4f}")
        elif isinstance(result, dict) and result.get("accuracy") is not None:
            print(f"[train] {args.model} -> accuracy reportada: {result['accuracy']:.4f}")
    else:
        print(f"El módulo '{args.model}' no expone run().")

if __name__ == "__main__":
    main()
