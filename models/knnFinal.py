#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNIVERSIDAD AUTÓNOMA DEL ESTADO DE MÉXICO
CU UAEM ZUMPANGO


Author: Dr. Asdrúbal López Chau

Descripción:  Ayuda Bryan Cisneros

Created on Tue Feb 15 16:14:15 2022

@author: asdruballopezchau
"""

import pandas as pd
from collections import Counter
from sklearn.neighbors import KNeighborsClassifier as KNN
from sklearn.model_selection import train_test_split as split
from sklearn.metrics import classification_report
import time
from sklearn.metrics import roc_curve, roc_auc_score, auc
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import LabelEncoder



datos = pd.read_excel("conjunto_de_datos_normalizados.xlsx")
c = Counter(datos.CARRERA_ACTUAL)
print(c)

X = datos.iloc[:, :-1]
y = datos.iloc[:, -1]

encoder = LabelEncoder()
encoder.fit(y)
encoded_Y = encoder.transform(y)

knn = KNN(5)
rand = int(time.time())
X_train, X_test, y_train, y_test = split(X, encoded_Y, 
                                         test_size=0.33, 
                                         random_state=rand)

knn.fit(X_train, y_train)
yp = knn.predict(X_test)

#target_names = list(set(encoded_Y))
target_names = ['class 0', 'class 1', 'class 2', 'class 3']
print(classification_report(y_test, yp, target_names=target_names))

y_scores = knn.predict_proba(X_test)

n_classes = 4

hot_y = np.zeros((y_test.size, y_test.max()+1))
hot_y[np.arange(y_test.size),y_test] = 1

# Compute ROC curve and ROC area for each class
fpr = dict()
tpr = dict()
roc_auc = dict()
for i in range(n_classes):
    fpr[i], tpr[i], _ = roc_curve(hot_y[:, i], y_scores[:, i])
    roc_auc[i] = auc(fpr[i], tpr[i])
    
# Compute micro-average ROC curve and ROC area
fpr["micro"], tpr["micro"], _ = roc_curve(hot_y.ravel(), y_scores.ravel())
roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

plt.figure()
lw = 2
plt.plot(
    fpr[2],
    tpr[2],
    color="darkorange",
    lw=lw,
    label="ROC curve (area = %0.2f)" % roc_auc[2],
)
plt.plot([0, 1], [0, 1], color="navy", lw=lw, linestyle="--")
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("KNN ROC AUC")
plt.legend(loc="lower right")
plt.show()


