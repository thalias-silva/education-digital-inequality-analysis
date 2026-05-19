{{ config(materialized='table') }}

SELECT 
    c.*
    -- ,
    -- i.idhm,
    -- i.idhm_renda,
    -- i.idhm_educacao,
    -- -- Criando a "Zona de Alerta": Município Pobre (IDHM < 0.6) + Exclusão Digital (SMED < 30)
    -- CASE 
    --     WHEN i.idhm < 0.6 AND c.SMED < 30 THEN 'Vulnerabilidade Crítica'
    --     WHEN i.idhm < 0.6 AND c.SMED >= 30 THEN 'Resiliência Digital'
    --     WHEN i.idhm >= 0.6 AND c.SMED < 30 THEN 'Atraso Tecnológico'
    --     ELSE 'Desenvolvimento Estável'
    -- END AS status_vulnerabilidade
FROM {{ ref('refined_censo_escolar') }} c
-- LEFT JOIN {{ ref('idhm_municipios') }} i ON c.CO_MUNICIPIO = i.codigo_municipio