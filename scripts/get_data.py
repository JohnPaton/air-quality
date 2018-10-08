import air_quality as aq
import click
import pandas as pd

RAW_DIR = "../data/raw/openaq"
DB_FILE = "../data/db/aq.db"
START_DATE = "2015-06-29"


def main(raw_dir, start_date, db_file):
    dates = aq.data_loading.generate_date_list(start_date)

    aq.data_loading.remove_most_recent_csvs(raw_dir, n=5)

    urls_fnames = aq.data_loading.get_download_params(dates, raw_dir)
    aq.data_loading.download_files(urls_fnames)

    paths = [x[1] for x in urls_fnames]
    aq.data_loading.load_amsterdam_from_csvs(paths, db_file)

    aq.data_loading.refresh_amsterdam_interim_table(db_file)


@click.command()
@click.option(
    "-r",
    "--raw_dir",
    type=click.Path(file_okay=False, dir_okay=True),
    default=RAW_DIR,
)
@click.option(
    "-d",
    "--db_file",
    type=click.Path(file_okay=True, dir_okay=False),
    default=DB_FILE,
)
@click.option("-a", "--download_all", is_flag=True)
def cli(raw_dir, db_file, download_all):
    if download_all:
        start = START_DATE
    else:
        today = pd.datetime.today()
        recent = today - pd.Timedelta(days=5)
        start = str(recent.date())

    main(raw_dir, start, db_file)


if __name__ == "__main__":
    cli()
