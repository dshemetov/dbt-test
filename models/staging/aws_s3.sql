-- models/staging/aws_s3.sql
{{
    config(
        enabled=has_aws_credentials()
    )
}}

SELECT *
FROM {{ source('aws_s3', 'raw_s3_data') }}