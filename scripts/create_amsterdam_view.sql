CREATE VIEW amsterdam_raw AS
SELECT * FROM raw
WHERE city = 'amsterdam' COLLATE NOCASE;
