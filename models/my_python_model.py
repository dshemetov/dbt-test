import pandas


def model(dbt, session):
    # Get data from an SQL model
    my_sql_model_df = dbt.ref("time_series_data_archive").to_df()

    # Transform with Pandas
    final_df = my_sql_model_df[(my_sql_model_df["value"] > 100)]

    # Return the transformed data
    return final_df
