#!/usr/bin/env bash

files=$(ls data/raw/openaq/*.csv)
for file in $files; do
    echo $file
    sqlite3 -csv data/db/aq.db ".import $file raw"
done
