# 🥪 The Jaffle Shop 🦘

## Delphi Testing Notes

### Setup

To setup, run

```sh
# Install uv https://github.com/astral-sh/uv
# This will install Python 3.11 (if you don't have it installed) with no system interference.
# It will also install the dependencies from pyproject.toml in a local .venv.
# Subsequent commands of `uv run ...` will use this virtual environment
uv sync
source .venv/bin/activate

# Alternatively, you can do this instead (and avoid the 'uv run' commands below)
# I personally have alias uvr="uv run" in my .zshrc to cut down on typing
python -m venv .venv
source .venv/bin/activate
pip install dbt-core dbt-duckdb dbt-metricflow

# Test that dbt works
dbt --version

# Update dbt packages
dbt deps

# Setup AWS credentials in your .env file (optional)
S3_ACCESS_KEY_ID=<your-access-key-id>
S3_SECRET_ACCESS_KEY=<your-secret-access-key>
```

### Documentation and DAG Visualization

```sh
# Generate and view documentation
# See the DAG by clicking the blue circle in the bottom right
dbt docs generate
dbt docs serve
```

### Loading Data and Building the Project

An example of how to load data and build the project.

```sh
# Load the data from './jaffle-data'
dbt seed

# Build the project
dbt build
```

As part of the build, the SQL is compiled and the models are materialized.
You can find the compiled SQL in the `target` folder.

### Viewing the Data

Building the project will create a `delphi_test.duckdb` file in the root of the project and populate it with the tables defined in this project.
You can view the data in the database with the following commands:

```sh
dbt show --select customers --limit 5
dbt show --select orders --limit 5
```

List the available objects that can be viewed

```sh
# This will show a bit too much info
dbt list

# You can filter by resource type
dbt list --resource-type source
dbt list --resource-type model
dbt list --resource-type metric
```

You can also query the database directly using the duckdb CLI.
You can get the self-contained duckdb executable for the CLI [here](https://duckdb.org/docs/installation/).
On Linux, it's as simple as

```sh
curl --fail --location --progress-bar --output duckdb_cli-linux-amd64.zip https://github.com/duckdb/duckdb/releases/download/v1.1.3/duckdb_cli-linux-amd64.zip && unzip duckdb_cli-linux-amd64.zip
```

Now you can see what tables are available in the database:

```sh
# Looking at the SQL-standard meta views
# https://duckdb.org/docs/sql/meta/information_schema
./duckdb delphi_test.duckdb -c "SELECT * FROM information_schema.tables"

# Same thing, but using DuckDB-specifics
# https://duckdb.org/docs/sql/meta/duckdb_table_functions
./duckdb delphi_test.duckdb -c "SELECT * FROM duckdb_tables;"
./duckdb delphi_test.duckdb -c "SELECT * FROM duckdb_views;"
```

You can also query one of the tables directly:

```sh
./duckdb delphi_test.duckdb -c "SELECT * FROM customers;"
```

### dbt Packages

This project uses the following dbt packages:

- [dbt-labs/dbt_utils](https://hub.getdbt.com/dbt-labs/dbt_utils/latest/)
- [calogica/dbt_date](https://hub.getdbt.com/calogica/dbt_date/latest/)
- [dbt-labs/dbt-audit-helper](https://github.com/dbt-labs/dbt-audit-helper)

dbt packages are defined in the `packages.yml` file.
I looked through the available packages and these seem to be the most useful.

### Testing the Data

The packages above include conditions in the model definitions that test the data.
You can run the tests with the following command:

```sh
dbt test
```

- See for instance `models/staging/stg_locations.yml` for an example of a data unit test.
- See for instance `models/staging/stg_customers.yml` for an example of a data test.

### dbt Structure Overview

- Raw data - data as it comes from the source (in this repo, `jaffle-data` seeds, but in a real-world scenario, this would be data from a data warehouse)
- Staging - data that has been cleaned and transformed (in this repo, `stg_customers`, `stg_orders`, etc.)
- Marts - data that has been aggregated and rolled up (in this repo, `customers`, `orders`, etc.)
- Snapshots - data that has been captured at a point in time (in this repo, `orders_snapshot`)

### Source Freshness

dbt can capture the freshness of the source data and produce warnings or errors if the data is stale.
One of the sources in `models/staging/__sources.yml` has a `freshness` block defined.

```sh
dbt source freshness
```

[Source Data Freshness Docs](https://docs.getdbt.com/docs/build/sources#source-data-freshness).

### Snapshots

dbt snapshots are a way to capture the state of a table at a point in time.
The way dbt handles this internally is very similar to how we do it in SQL.

```sh
# Create some time series data
python source_data.py --create-time-series-data

# Run the snapshot
dbt snapshot

# Inspect the snapshot table
dbt show --select time_series_data_archive

# Or with DuckDB
./duckdb delphi_test.duckdb -c "SELECT * FROM time_series_data_archive;"
```

[Snapshots Docs](https://docs.getdbt.com/docs/build/snapshots).

### Incremental Models

Incremental models will only perform operations on rows that are new or have changed since the last time the model was run.
This is a way to make models more efficient.

An example can be found in `models/staging/incremental_copy.sql`:

```sh
# Load some synthetic data into the `source_data` table in DuckDB
python source_data.py --create-source-data

# Show what the model will do with this data
dbt show --select incremental_copy

# Run the model
dbt run --select incremental_copy

# Run the model again (should see no rows updated)
dbt run --select incremental_copy

# Update the source data with more rows
python source_data.py --add-data

# Show what the model will do again (should see more rows)
dbt show --select incremental_copy

# Run the model again
dbt run --select incremental_copy

# Run the model and ignore the incremental model, refreshing the entire table
dbt run --select incremental_copy --full-refresh
```

This can be extended to handle more complex cases, such as updating a row if the value changes, or deleting a row if it is no longer present in the source.

[Incremental models docs](https://docs.getdbt.com/docs/build/incremental-models-overview)

### Python Integration

dbt also supports writing Python code in models.
See the example in `models/my_python_model.py` and `models/my_python_model.yml`.

```sh
# Install Pandas in your .venv (if you're not using uv)
pip install pandas

# To execute
dbt run --select my_python_model

# For some reason, this errors out
dbt show --select my_python_model

# This works
./duckdb delphi_test.duckdb -c "SELECT * FROM my_python_model;"
```

The docs say that this feature is mostly intended for developer convenience and for small files.
Anything that needs to be performant should be done in SQL.

[Python models docs](https://docs.getdbt.com/docs/build/python-models)

### Dagster Integration

WIP. Working off [this example](https://docs.dagster.io/integrations/libraries/dbt/transform-dbt).

```sh
# Install Dagster in your .venv (if you're not using uv)
pip install dagster plotly dagster-dbt dagster-webserver

# Run the Dagster UI
dagster dev
```

### AWS S3

This project includes an example of how to load data from an S3 bucket.
See `models/staging/aws_s3.sql` for the model definition.
There's also a macro in `macros/has_aws_credentials.sql` that is used to enable the model if AWS credentials for the forecasting-team-data bucket are available.

### Using the Semantic Layer (optional)

Use the built-in metrics with MetricFlow (part of the Semantic Layer, a way to systematize and organize metrics)

```sh
# List available metrics (see e.g. bottom of `customers.yml` for examples of how these are defined)
mf list metrics

# Query the metrics
mf query --metrics count_lifetime_orders --group-by customer
```

### Reading Suggestions

- [Best Practices for Structuring dbt Projects](https://docs.getdbt.com/best-practices/how-we-structure/1-guide-overview)
- [dbt Commands](https://docs.getdbt.com/reference/dbt-commands)
- [Materializations](https://docs.getdbt.com/docs/build/materializations)
- [What are configs?](https://docs.getdbt.com/reference/configs-and-properties)
- [What are incremental models?](https://docs.getdbt.com/docs/build/incremental-models-overview)
- [dbt and Airflow](https://www.getdbt.com/blog/dbt-airflow)
- [dbt and Dagster](https://docs.dagster.io/integrations/libraries/dbt/)

For the default docs for the template behind this project, see: https://github.com/dbt-labs/jaffle-shop.
