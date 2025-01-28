-- models/incremental_copy.sql
{{
    config(
        materialized='incremental',
        unique_key='id'
    )
}}

select
    id,
    value,
    created_at
from {{ source('raw_incremental', 'source_data') }}
{% if is_incremental() %}
    -- https://docs.getdbt.com/reference/dbt-jinja-functions/this
    where created_at > (select coalesce(max(created_at), '1900-01-01') from {{ this }})
{% endif %}