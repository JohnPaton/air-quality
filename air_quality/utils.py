import pandas as pd
import pickle


def flatten_column_names(cols, remove=""):
    """
    Turn multi-level DataFrame columns into single-level, joined by underscores.

    Args:
        cols: The multilevel df.columns
        remove: An optional string to delete from the name (e.g. something
            shared by all columns)

    Returns:
        list: the new column names

    """
    col_pairs = cols.ravel()

    new_cols = ["_".join(cp) for cp in col_pairs]
    new_cols = [c.replace(remove, "") for c in new_cols]

    return new_cols


def df_like(df, data):
    """Create a new DataFrame with the same index and columns as `df`, but
    containing the new `data`. Shapes must match."""
    return pd.DataFrame(index=df.index, columns=df.columns, data=data)


def load_model_objects(model_dir):
    with open(model_dir + "/X_scaler.pkl", "rb") as h:
        X_scaler = pickle.load(h)

    with open(model_dir + "/y_scaler.pkl", "rb") as h:
        y_scaler = pickle.load(h)

    with open(model_dir + "/pca.pkl", "rb") as h:
        pca = pickle.load(h)

    with open(model_dir + "/model.pkl", "rb") as h:
        model = pickle.load(h)

    return X_scaler, y_scaler, pca, model


def date_series_to_dict(ser: pd.Series):
    ser_dict = ser.to_dict()
    ser_dict = {str(dt.date()): v for dt, v in ser_dict.items()}
    return ser_dict
