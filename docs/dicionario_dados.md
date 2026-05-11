# Dicionário de Dados - Projeto SMED

## Objetivo
Mapear as variáveis das bases INEP, IBGE e CETIC para a construção do Score Multidimensional de Exclusão Digital (SMED). [cite: 31, 161]

## Camada Trusted (MinIO)
- **Filtro de Escolas:** Inclusão apenas de escolas com `TP_SITUACAO_FUNCIONAMENTO = 1` (Escolas em Atividade). [cite: 172]
- **Formato:** Parquet.

## Camada Refined (dbt)
- **Normalização:** Variáveis contínuas (como densidade de computadores) serão normalizadas via **Z-score**. [cite: 57, 177]
- **Tradução:** Uso de tabelas de referência para transformar códigos numéricos em descrições legíveis (Sim/Não). [cite: 189]
