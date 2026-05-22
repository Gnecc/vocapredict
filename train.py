import argparse
from models.factory import load_model_module

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=["svm","knn","rf","nn","kmeans","fcm","pca"], default="svm")
    parser.add_argument(
        "--dataset",
        default="conjunto_de_datos_reetiquetados.xlsx",
        help="Dataset real CSV o XLSX usado para entrenar.",
    )
    args = parser.parse_args()

    mod = load_model_module(args.model)

    if hasattr(mod, "run"):
        result = mod.run(args.dataset)
        if isinstance(result, dict) and result.get("auc_ovr") is not None:
            print(f"[train] {args.model} -> AUC(OvR) reportado: {result['auc_ovr']:.4f}")
        elif isinstance(result, dict) and result.get("accuracy") is not None:
            print(f"[train] {args.model} -> accuracy reportada: {result['accuracy']:.4f}")
    else:
        print(f"El módulo '{args.model}' no expone run().")

if __name__ == "__main__":
    main()
