# models/svmFinal.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from sklearn import svm
from sklearn.metrics import roc_curve, auc, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import label_binarize, LabelEncoder
from sklearn.multiclass import OneVsRestClassifier
import pandas as pd
import joblib

def run():
    # Carga de datos
    dataframe = pd.read_excel('conjunto_de_datos_normalizados.xlsx')

    X = dataframe.iloc[:, :-1]
    Y = dataframe.iloc[:, -1]

    encoder = LabelEncoder().fit(Y)
    y = encoder.transform(Y)

    X = np.array(X, dtype=float)
    n_classes = len(np.unique(y))

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.5, random_state=0, stratify=y
    )

    classifier = OneVsRestClassifier(
        svm.SVC(kernel="linear", probability=True, random_state=0)
    )
    y_score = classifier.fit(X_train, y_train).decision_function(X_test)

    joblib.dump(classifier, "svm_model.joblib")
    joblib.dump(encoder, "label_encoder.joblib")
    print("Modelo y encoder guardados.")

    # Para ROC multiclase, binarizamos y_test
    Y_test_bin = label_binarize(y_test, classes=np.arange(n_classes))

    fpr, tpr, roc_auc = {}, {}, {}
    for i in range(n_classes):
        fpr[i], tpr[i], _ = roc_curve(Y_test_bin[:, i], y_score[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])

    fpr["micro"], tpr["micro"], _ = roc_curve(Y_test_bin.ravel(), y_score.ravel())
    roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

    auc_ovr = None
    try:
        auc_ovr = roc_auc_score(Y_test_bin, y_score, multi_class="ovr")
        print(f"AUC (OvR): {auc_ovr:.4f}")
    except Exception:
        pass

    # Grafica una clase (ajusta idx si quieres otra)
    idx = 0 if 0 in roc_auc else list(roc_auc.keys())[0]
    plt.figure()
    lw = 2
    plt.plot(fpr[idx], tpr[idx], lw=lw, label="ROC clase %d (área = %0.2f)" % (idx, roc_auc[idx]))
    plt.plot([0, 1], [0, 1], lw=lw, linestyle="--")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("SVM ROC AUC (One-vs-Rest)")
    plt.legend(loc="lower right")
    plt.show()

    return {"auc_ovr": auc_ovr, "classes": n_classes}

if __name__ == "__main__":
    run()
