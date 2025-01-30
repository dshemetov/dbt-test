import duckdb
import sys

con = duckdb.connect("delphi_test.duckdb")

create_source_data = """
-- source_data.sql
CREATE OR REPLACE TABLE source_data AS
SELECT
    ROW_NUMBER() OVER () as id,
    ROUND(RANDOM() * 1000)::INTEGER as value,
    TIMESTAMP '2024-01-01 00:00:00' +
        INTERVAL '1 hour' * (ROW_NUMBER() OVER ())::INTEGER as created_at
FROM range(100);
"""

add_data = """
INSERT INTO source_data
SELECT
    ROW_NUMBER() OVER () + 100 as id,
    ROUND(RANDOM() * 1000)::INTEGER as value,
    TIMESTAMP '2024-01-05 00:00:00' +
        INTERVAL '1 hour' * (ROW_NUMBER() OVER ())::INTEGER as created_at
FROM range(50);
"""

create_time_series_data = """
CREATE OR REPLACE TABLE time_series_data AS
SELECT
    DATETIME '2024-01-01' +
        INTERVAL '1 day' * (ROW_NUMBER() OVER ())::INTEGER as reference_date,
    ROUND(RANDOM() * 1000)::INTEGER as value
FROM range(10);
"""

add_time_series_data = """
INSERT INTO time_series_data
SELECT
    DATETIME '2024-01-05' +
        INTERVAL '1 day' * (ROW_NUMBER() OVER ())::INTEGER as reference_date,
    ROUND(RANDOM() * 1000)::INTEGER as value
FROM range(10);
"""

if __name__ == "__main__":
    # If --create-source-data is passed, create the source data
    if "--create-source-data" in sys.argv:
        con.sql(create_source_data)

    # If --show-data is passed, show the data
    if "--show-data" in sys.argv:
        print(con.sql("SELECT * FROM source_data"))

    # If --add-data is passed, add more data
    if "--add-data" in sys.argv:
        con.sql(add_data)

    if "--create-time-series-data" in sys.argv:
        con.sql(create_time_series_data)

    if "--add-time-series-data" in sys.argv:
        con.sql(add_time_series_data)
