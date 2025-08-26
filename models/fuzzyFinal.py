#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 19 23:30:16 2022

@author: bryanedoardocisnerosbravo
"""

%matplotlib inline
import numpy as np
from fcmeans import FCM
from matplotlib import pyplot as plt
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import roc_curve, roc_auc_score, auc


dataframe = pd.read_excel('conjunto_de_datos_normalizados.xlsx');
dataset = dataframe.values

X = dataframe.iloc[:, :-1]
Y = dataframe.iloc[:, -1]

encoder = LabelEncoder()
encoder.fit(Y)
encoded_Y = encoder.transform(Y)

X = np.array(X);

fcm = FCM(n_clusters=4)
fcm.fit(X)

# outputs
fcm_centers = fcm.centers
fcm_labels = fcm.predict(X)

# plot result
f, axes = plt.subplots(1, 2, figsize=(11,5))
axes[0].scatter(X[:,0], X[:,1], alpha=.1)
axes[1].scatter(X[:,0], X[:,1], c=fcm_labels, alpha=.1)
axes[1].scatter(fcm_centers[:,0], fcm_centers[:,1], marker="+", s=500, c='r')
plt.show()

n_classes = 4

hot_y = np.zeros((encoded_Y.size, encoded_Y.max()+1))
hot_y[np.arange(encoded_Y.size),encoded_Y] = 1

y_scores = np.zeros((fcm_labels.size, fcm_labels.max()+1))
y_scores[np.arange(fcm_labels.size),fcm_labels] = 1

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
plt.title("Fuzzy ROC AUC")
plt.legend(loc="lower right")
plt.show()