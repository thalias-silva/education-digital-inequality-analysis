WITH 
metricas AS (
    SELECT 
        nu_ano_censo,
        sg_uf, 
        dependencia_adm,
        localizacao,
        -- QWUANTIDADE DE ESCOLAS POR PERFIL DE USO TECNOLÓGICO
        COUNT(CASE WHEN perfil_uso_tecnologico = 'Conectividade Pedagogica Plena' THEN 1 END) AS escolas_conectividade_pedagogica_plena,
        COUNT(CASE WHEN perfil_uso_tecnologico = 'Conexao Sem Dispositivos' THEN 1 END) AS escolas_conexao_sem_dispositivos,
        COUNT(CASE WHEN perfil_uso_tecnologico = 'Internet Apenas Administrativa' THEN 1 END) AS escolas_internet_apenas_administrativa,
        COUNT(CASE WHEN perfil_uso_tecnologico = 'Sem Conectividade' THEN 1 END) AS escolas_sem_conectividade,
        COUNT(CASE WHEN perfil_uso_tecnologico = 'Conectividade e Uso Tecnologico Indefinidos' THEN 1 END) AS escolas_conectividade_uso_indefinidos,  
        SUM(total_dispositivos_aluno)/SUM(matricula_fund_med) AS densidade_tecnologica_total

    FROM {{ ref('refined_censo_escolar') }}
    GROUP BY 1, 2, 3, 4
)
    SELECT *
    FROM metricas