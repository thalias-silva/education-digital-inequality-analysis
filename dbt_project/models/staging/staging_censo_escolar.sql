{{ config(materialized='view') }}

with raw_data as (
    -- Esta parte traz os dados brutos do seu MinIO
    select * from {{ source('minio_raw', 'censo_trusted_parquet') }}
)

select
    -- Aqui você pode filtrar ou renomear colunas no futuro
    *
from raw_data