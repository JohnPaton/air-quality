CREATE TABLE raw(
    location TEXT,
    city TEXT,
    country TEXT,
    utc TEXT,
    local TEXT,
    parameter TEXT,
    value REAL,
    unit TEXT,
    latitude REAL,
    longitude REAL,
    attribution TEXT,
    --- Don't allow duplicate records
    UNIQUE(location, city, country, utc, parameter)
);
