#! /usr/env/python

import flask
from flask import jsonify

import pandas as pd
import click
import sqlite3

import air_quality as aq


### Defaults (can be overwritten with cli)
class Config:
    DB_FILE = "data/db/aq.db"
    MODEL_DIR = "models/v0"
    TARGET = "pm10_Vondelpark"
    LOOKBACK = 2


app = flask.Flask("air_quality")


@app.route("/predict", strict_slashes=False)
def predict_latest():
    conn = sqlite3.connect(Config.DB_FILE)

    df = pd.read_sql(
        "SELECT * FROM amsterdam_interim ORDER BY local DESC LIMIT 5;",
        conn,
        index_col="local",
    )

    conn.close()
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    X_scaler, y_scaler, pca, model = aq.utils.load_model_objects(
        Config.MODEL_DIR
    )

    X, y, _, _, _ = aq.data_processing.interim_to_training_set(
        df, Config.TARGET, X_scaler, y_scaler, pca, lookback=Config.LOOKBACK
    )

    values = aq.modelling.predict_values(
        X, df[Config.TARGET].loc[X.index], model, y_scaler
    )

    values = values.iloc[-1:]
    return jsonify(aq.utils.date_series_to_dict(values))


@click.command()
@click.option(
    "-m",
    "--model_dir",
    help="Directory where model objects are picked",
    type=click.Path(dir_okay=True, file_okay=False, exists=True),
)
@click.option(
    "-d",
    "--db_file",
    help="Path to sqlite database",
    type=click.Path(dir_okay=False, exists=True),
)
def cli(model_dir, db_file):

    if db_file is not None:
        Config.DB_FILE = db_file

    if model_dir is not None:
        Config.MODEL_DIR = model_dir

    app.run(host="0.0.0.0", debug=True)


if __name__ == "__main__":
    cli()
