import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import LeaveOneOut as LOOCV
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_absolute_error

''' loo = LOOCV()
        loo.get_n_splits(X)
        metrics = np.array([])
        model = LogisticRegression()

        for i, (train_index, test_index) in enumerate(loo.split(X)):
            print(f"Fold {i}:")
            print(f"Train: index = {train_index}")
            print(f"Test: index = {test_index}")
        
        model.fit()'''

class EventsPredictor:

    def __init__(self):
        pass

    def predict(self, filepath: str, q: str) -> str:

        # goal: predict satisification value given random 

        df = pd.DataFrame(pd.read_csv(filepath))
        X = OneHotEncoder().fit_transform(df[q].to_frame())
        y = df["Satisfaction with Waltham Chamber of Commerce"]

        loo = LOOCV()
        loo.get_n_splits(X)
        metrics = []
        preds = []
        model = LogisticRegression()

        for train_index, test_index in loo.split(X):
            
            print(f"Train: index = {train_index}")
            print(f"Test: index = {test_index}")

            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]

            model.fit(X_train, y_train)
            pred = model.predict(X_test)

            preds.append(pred)

            metric = mean_absolute_error(y_test, pred)
            metrics.append(metric)

        return f"MSE: {np.mean(metrics)}\nPredictions: {preds}\n"

p = EventsPredictor()
print(p.predict("C:\\Users\\adria\\Downloads\\DeisHacks (Responses) - Form Responses 1 (1).csv", "How long have you been a member?"))
