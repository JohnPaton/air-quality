# Air Quality Prediction

## Installation
To create a virtual environment and install the required packages, run

```bash
$ make venv
```

Note that you should have Python 3.6 and virtualenv available.


## Data

The raw data from [OpenAQ](https://openaq.org/) is available on s3 at https://openaq-data.s3.amazonaws.com. To download the raw data up to the most recent available measurements on s3, use

```bash
$ make data
```

This calls the script `scripts/get_data.py`, which will remove the 2 most recent files in `data/raw/openaq` (as they may have been updated), and then re-download that file and all more recent files which have not yet been downloaded.
