import pandas as pd
import numpy as np
import scipy.stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from . import utils

DROP_LOCATIONS = ["Amsterdam-A10 west", "Amsterdam-Jan van Galenstraat"]
KEEP_PARAMETERS = ["pm10", "pm25"]
DROP_COLUMNS = ["unit", "city", "attribution", "utc", "country"]


def slope(ser):
    """Calculate the slope of DateTime-indexed series in units per day
    using linear regression."""

    if len(ser) <= 1:
        return 0.

    ns_per_day = 1e9 * 3600 * 24

    x = ser.index.astype(int) / ns_per_day
    y = ser.values

    results = scipy.stats.linregress(x, y)
    return results[0]


def add_lookback_columns(df: pd.DataFrame, n, suffix="_t-"):
    """
    Lag dataframe columns and add them to the original dataframe.

    Note that the first `n` entries will contain NaNs due to lagging.

    Args:
        df: the dataframe to lag
        n: the number of period to lag
        suffix: New column will be named <column name><suffix><number of lags>,
            for example "temperature_t-3"

    Returns: the dataframe with added columns

    """
    df_out = df.copy()

    for lag in range(1, n + 1):
        df_lag = df.shift(lag)
        new_col_names = [f"{c}{suffix}{lag}" for c in df.columns]
        df_lag.columns = new_col_names

        df_out[new_col_names] = df_lag

    return df_out


def raw_to_interim(df: pd.DataFrame):
    """
    Unpivot the raw OpenAQ data and make some selections.

    Args:
        df: DataFrame
        The raw data provided by OpenAQ, see
        https://openaq-data.s3.amazonaws.com/index.html

    Returns:
        Daily mean and slope of pm10 and pm25 at locations except those in
        DROP_LOCATIONS. Column names are of form <parameter>_<location>[_der].

    """

    assert "location" in df.columns, "DataFrame doesn't have 'location' column"

    # initial filters
    df = df[~df["location"].isin(DROP_LOCATIONS)]
    df = df[df["parameter"].isin(KEEP_PARAMETERS)]
    df = df.drop(columns=DROP_COLUMNS, axis=1)

    # reshape
    df_pivoted = pd.pivot_table(
        df.reset_index(drop=False),
        index="local",
        columns=["parameter", "location"],
        values="value",
    )

    df_pivoted.columns = utils.flatten_column_names(
        df_pivoted.columns, remove="Amsterdam-"
    )

    # remove invalid values
    df_pivoted[df_pivoted < 0] = np.nan
    df_pivoted = df_pivoted.sort_index()
    df_pivoted = df_pivoted.ffill()

    # aggregate daily means
    df_datetime = df_pivoted
    df_datetime.index = pd.to_datetime(df_datetime.index)

    df_resampled = df_datetime.resample("1d")
    df_agg = df_resampled.mean().ffill()
    df_agg = df_agg.dropna()

    # aggregate daily slopes
    df_der = df_resampled.apply({col: slope for col in df_datetime.columns})
    df_der.columns = [c + "_der" for c in df_der.columns]
    df_der = df_der.fillna(0)

    df_agg[df_der.columns] = df_der.loc[df_agg.index]

    return df_agg


def interim_to_training_set(
    df: pd.DataFrame,
    target,
    X_scaler=None,
    y_scaler=None,
    pca_transformer=None,
    pca_components=None,
    lookback=0,
):
    """
    Convert the output of `raw_to_interim()` to a machine learning training set.
    Data is differenced and scaled. Lookback can be applied to add lagged data
    as new columns. PCA transformation is performed and `pca_components`
    features are kept.


    The last row of `y` will be NaN since we can't see beyond the end of the
    data. The first `lookback+1` rows of X will be dropped due to
    differencing and looking back.

    Fit transformers are also returned for performing inverse transforms.

    Args:
        df: The processed data
        target: Column to predict
        X_scaler: transformer to rescale the differenced data
        y_scaler: transformer to rescale the differenced target
        pca_transformer:
        pca_components: number of PCA components to keep
        lookback: number of periods of lag to add as new columns

    Returns:
        X, y, X_scaler, y_scaler, pca_transformer
    """

    # difference
    df = df.diff()
    df = df.iloc[1:]

    # scale
    if X_scaler is None:
        X_scaler = StandardScaler().fit(df)

    if y_scaler is None:
        y_scaler = StandardScaler().fit(df[[target]])

    y = y_scaler.transform(df[[target]].shift(-1))

    df = utils.df_like(df, X_scaler.transform(df))

    # lookback
    if lookback:
        df = add_lookback_columns(df, lookback)
        df = df.iloc[lookback:]
        y = y[lookback:]

    # PCA
    if pca_transformer is None:
        pca_transformer = PCA(n_components=pca_components).fit(df)

    X = pd.DataFrame(index=df.index, data=pca_transformer.transform(df))
    y = pd.Series(y.flatten(), index=df.index)

    if pca_components is not None and X.shape[1] > pca_components:
        X = X[:, :pca_components]

    return X, y, X_scaler, y_scaler, pca_transformer
