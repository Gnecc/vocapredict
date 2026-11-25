import argparse
import inspect
from models.factory import load_model_module

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=["riasec","svm","knn","rf","nn","kmeans","fcm","pca"], default="riasec")
    parser.add_argument(
        "--dataset",
        default=None,
        help="Dataset CSV o XLSX usado para entrenar; el predeterminado depende del modelo.",
    )
    parser.add_argument(
        "--augment-train",
        action="store_true",
        help="Aplica aumento sintetico adicional solo al split de entrenamiento.",
    )
    args = parser.parse_args()

    if args.model == "riasec":
        if args.augment_train:
            parser.error("El entrenamiento RIASEC no usa aumento sintético.")
        from models.riasec import DATASET, run
        run(args.dataset or DATASET)
        return

    mod = load_model_module(args.model)
    dataset = args.dataset or "data/conjunto_de_datos_aumentado_75_sintetico_amai.csv"

    if hasattr(mod, "run"):
        run_signature = inspect.signature(mod.run)
        if "augment_train" in run_signature.parameters:
            result = mod.run(dataset, augment_train=args.augment_train)
        else:
            result = mod.run(dataset)
        if isinstance(result, dict) and result.get("auc_ovr") is not None:
            print(f"[train] {args.model} -> AUC(OvR) reportado: {result['auc_ovr']:.4f}")
        elif isinstance(result, dict) and result.get("accuracy") is not None:
            print(f"[train] {args.model} -> accuracy reportada: {result['accuracy']:.4f}")
    else:
        print(f"El módulo '{args.model}' no expone run().")

if __name__ == "__main__":
    main()
