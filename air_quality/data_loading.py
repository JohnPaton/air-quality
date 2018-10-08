import sqlite3
import pandas as pd
import glob
import tqdm
import os
import requests

from . import data_processing


def generate_date_list(start_date="2015-06-29"):
    # first file on https://openaq-data.s3.amazonaws.com is "2015-06-29"
    date_fmt = "%Y-%m-%d"
    # datetime objects
    dates = pd.date_range(
        start_date, pd.datetime.today() + pd.Timedelta(days=1)
    )

    date_strs = [d.strftime(date_fmt) for d in dates]  # strings

    return date_strs


def remove_most_recent_csvs(raw_dir, n=1):
    # get rid of last n downloaded files
    # (probably incomplete/day wasn't over yet)
    existing_files = list(sorted(glob.glob(os.path.join(raw_dir, "*.csv"))))
    if existing_files:
        for fname in existing_files[-n:]:
            os.remove(fname)
            print("Removed", fname.split("/")[-1])

    return existing_files[-n:]


def get_download_params(dates, raw_dir):
    # pairs of (url, filename) for downloading and saving raw data
    base_url = "https://openaq-data.s3.amazonaws.com/{}.csv"
    base_fname = raw_dir + "/{}.csv"

    # pairs of (url, filename) for downloading data
    urls_fnames = [(base_url.format(d), base_fname.format(d)) for d in dates]

    # skip existing files
    urls_fnames_filtered = [
        tpl for tpl in urls_fnames if not os.path.isfile(tpl[1])
    ]

    return urls_fnames_filtered


def download_files(urls_fnames):
    print("Downloading files...")
    pbar = tqdm.tqdm(urls_fnames, dynamic_ncols=True)
    for url, fname in pbar:
        cur_date = url.split("/")[-1][:-4]
        pbar.set_description("Now on {}".format(cur_date))
        response = requests.get(url)
        with open(fname, "w") as h:
            h.write(response.text)


def load_amsterdam_from_csvs(csv_paths, db_file):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    for fpath in tqdm.tqdm(csv_paths):
        df = pd.read_csv(fpath, dtype="str")
        if "city" not in df.columns:
            continue

        df = df[df["city"] == "Amsterdam"]
        if not len(df):
            continue

        qmarks = ",".join(len(df.columns) * ["?"])

        cur.executemany(
            f"INSERT OR IGNORE INTO amsterdam_raw VALUES ({qmarks})",
            df.values.tolist(),
        )

        conn.commit()

    conn.close()


def refresh_amsterdam_interim_table(db_file):
    conn = sqlite3.connect(db_file)
    df = pd.read_sql("SELECT * FROM amsterdam_raw;", conn)
    df_interim = data_processing.raw_to_interim(df)
    df_interim.to_sql("amsterdam_interim", conn, if_exists="replace")
    conn.close()
