from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

import numpy as np
import pandas as pd


def values_from_differences(values, differences, scaler=None, timestep="1d"):
    num_predictions = differences.shape[0]
    assert values.shape[0] >= num_predictions

    if scaler is not None:
        diffs = scaler.inverse_transform(differences)
    else:
        diffs = differences

    output = values.iloc[:num_predictions] + diffs
    output.index += pd.Timedelta(timestep)
    return output


def predict_values(X, real_values, model, y_scaler=None):
    y_pred = model.predict(X)
    y_values = values_from_differences(real_values, y_pred, y_scaler)
    return y_values
