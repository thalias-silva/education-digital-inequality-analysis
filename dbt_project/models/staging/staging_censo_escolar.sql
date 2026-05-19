{{ config(materialized='view') }}

with raw_data as (
    -- Lendo diretamente do MinIO de forma estável
    select * from read_parquet('s3://trusted/censo_escolar/censo_trusted.parquet')
)

select
    *
from raw_data
where TP_SITUACAO_FUNCIONAMENTO = 1  -- Filtro para trazer apenas escolas ativas