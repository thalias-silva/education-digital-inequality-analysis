{{ config(materialized='view') }}

with raw_data as (
    -- Esta parte traz os dados brutos do seu MinIO
    select * from {{ source('minio_raw', 'censo_trusted_parquet') }}
)

    select
        *
    from raw_data
    where TP_SITUACAO_FUNCIONAMENTO = 1  -- ESTE FILTRO PARA TRAZER DADOS APENAS DE ESCOLAS ATIVAS
