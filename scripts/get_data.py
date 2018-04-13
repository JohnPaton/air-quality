import os
import glob
import pandas as pd
import requests
from tqdm import tqdm


def generate_dates():
    # first file on https://openaq-data.s3.amazonaws.com
    start_date = '2015-06-29'
    date_fmt = '%Y-%m-%d'
    dates = pd.date_range(start_date, pd.datetime.today())  # datetime objects
    date_strs = [d.strftime(date_fmt) for d in dates]  # strings

    return date_strs


def remove_most_recent():
    # get rid of last downloaded file (probably incomplete/day wasn't over yet)
    existing_files = list(sorted(glob.glob('../data/raw/openaq/*.csv')))
    if existing_files:
        for fname in existing_files[-2:]:
            os.remove(fname)
            print('Removed', fname.split('/')[-1])


def get_download_params(dates):
    # pairs of (url, filename) for downloading and saving raw data
    base_url = 'https://openaq-data.s3.amazonaws.com/{}.csv'
    base_fname = '../data/raw/openaq/{}.csv'

    # pairs of (url, filename) for downloading data
    urls_fnames = [(base_url.format(d), base_fname.format(d),) for d in dates]

    # skip existing files
    urls_fnames_filtered = [tpl for tpl in urls_fnames
                           if not os.path.isfile(tpl[1])]

    return urls_fnames_filtered


def download_files(urls_fnames):
    print('Downloading files...')
    pbar = tqdm(urls_fnames, dynamic_ncols=True)
    for url, fname in pbar:
        cur_date = url.split('/')[-1][:-4]
        pbar.set_description('Now on {}'.format(cur_date))
        response = requests.get(url)
        with open(fname, 'w') as h:
            h.write(response.text)


def main():
    dates = generate_dates()
    remove_most_recent()
    urls_fnames = get_download_params(dates)
    download_files(urls_fnames)


if __name__ == '__main__':
    main()
