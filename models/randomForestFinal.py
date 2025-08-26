#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 26 14:49:58 2022
#Ref https://www.codementor.io/@agarrahul01/multiclass-classification-using-random-forest-on-scikit-learn-library-hkk4lwawu
@author: bryanedoardocisnerosbravo
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc
import joblib as jb
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt

print('Libraries Imported')



#dataframe = read_csv("alumnos.csv")
dataframe = pd.read_excel('conjunto_de_datos_normalizados.xlsx');
dataset = dataframe.values
#X = dataset[:,0:9].astype(float)
#Y = dataset[:,9]
X = dataframe.iloc[:, :-1]
Y = dataframe.iloc[:, -1]

encoder = LabelEncoder()
encoder.fit(Y)
y = encoder.transform(Y)

#Creating the dependent variable class
factor = pd.factorize(y)
y = factor[0]
definitions = factor[1]
#print(y.head())
print(definitions)

# Creating the Training and Test set from data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.25, random_state = 21)

# Feature Scaling
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)
# Fitting Random Forest Classification to the Training set
classifier = RandomForestClassifier(n_estimators = 10, criterion = 'entropy', random_state = 42)
classifier.fit(X_train, y_train)

# Predicting the Test set results
y_pred = classifier.predict(X_test)
#Reverse factorize (converting y_pred from 0s,1s and 2s to Iris-setosa, Iris-versicolor and Iris-virginica
reversefactor = dict(zip(range(4),definitions))
y_test = np.vectorize(reversefactor.get)(y_test)
y_pred = np.vectorize(reversefactor.get)(y_pred)

# Making the Confusion Matrix
print(pd.crosstab(y_test, y_pred, rownames=['Actual classes'], colnames=['Predicted Classes']))

print(list(zip(dataframe.columns[0:9], classifier.feature_importances_)))
jb.dump(classifier, 'randomforestmodel.pkl') 

#target_names = list(set(encoded_Y))
target_names = ['class 0', 'class 1', 'class 2', 'class 3']
print(classification_report(y_test, y_pred, target_names=target_names))


n_classes = 4

hot_y = np.zeros((y_test.size, y_test.max()+1))
hot_y[np.arange(y_test.size),y_test] = 1

hot_labels = np.zeros((y_pred.size, y_pred.max()+1))
hot_labels[np.arange(y_pred.size),y_pred] = 1

# Compute ROC curve and ROC area for each class
fpr = dict()
tpr = dict()
roc_auc = dict()
for i in range(n_classes):
    fpr[i], tpr[i], _ = roc_curve(hot_y[:, i], hot_labels[:, i])
    roc_auc[i] = auc(fpr[i], tpr[i])
    
# Compute micro-average ROC curve and ROC area
fpr["micro"], tpr["micro"], _ = roc_curve(hot_y.ravel(), hot_labels.ravel())
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
plt.title("Random Forest ROC AUC")
plt.legend(loc="lower right")
plt.show()