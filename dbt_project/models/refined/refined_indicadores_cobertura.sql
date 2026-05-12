{{ config(materialized='table') }}

SELECT
    SG_UF,
    dependencia_adm,
    COUNT(CO_ENTIDADE) AS total_escolas,
    
    -- 1. Percentual de alcance total (Conectividade Básica)
    ROUND(SUM(IN_INTERNET) * 100.0 / COUNT(CO_ENTIDADE), 2) AS pct_escolas_com_internet,

    -- 2. Percentual que chega no aluno (Conectividade Pedagógica)
    ROUND(SUM(IN_INTERNET_ALUNOS) * 100.0 / COUNT(CO_ENTIDADE), 2) AS pct_escolas_com_internet_alunos,
    
    -- 3. O GAP (Diferença direta em pontos percentuais entre os dois indicadores)
    ROUND((SUM(IN_INTERNET) - SUM(IN_INTERNET_ALUNOS)) * 100.0 / COUNT(CO_ENTIDADE), 2) AS gap_perda_pedagogica,
    
    -- 4. Taxa de Conversão: Das que têm internet, quantas entregam ao aluno?
    ROUND(SUM(IN_INTERNET_ALUNOS) * 100.0 / NULLIF(SUM(IN_INTERNET), 0), 2) AS taxa_conversao_pedagogica,

    -- 5. Média de Densidade (Equipamentos por 100 alunos)
    ROUND(AVG(densidade_tecnologica_total), 2) AS densidade_media_100_alunos,
    
    -- 6. Perfil de Uso Majoritário (A categoria mais frequente no grupo)
    MODE(perfil_uso_tecnologico) AS perfil_mais_comum

FROM {{ ref('refined_censo_escolar') }}
GROUP BY 1, 2
ORDER BY SG_UF, dependencia_adm