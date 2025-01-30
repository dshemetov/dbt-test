{{ config(materialized='ephemeral') }}

select * from {{ source('raw_time_series', 'time_series_data') }}