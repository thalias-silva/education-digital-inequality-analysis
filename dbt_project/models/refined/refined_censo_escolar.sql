{{ config(materialized='table') }}

WITH dados_brutos AS (
    SELECT
        -- Identificação
        c.CO_ENTIDADE,
        c.NU_ANO_CENSO,
        c.SG_UF,
        c.NO_MUNICIPIO,
        c.CO_MUNICIPIO,
        c.NO_REGIAO,
        
        -- Tradução da Dependência e Localização
        dep.descricao as dependencia_adm,
        loc.descricao as localizacao,
        
        -- Tradução dos campos de infraestrutura tecnológica
        sn_int.descricao               AS possui_internet,
        sn_int_alu.descricao           AS internet_alunos,
        sn_banda.descricao             AS possui_banda_larga,
        sn_comp.descricao              AS possui_computador,
        sn_acesso_comp.descricao       AS acesso_internet_computador,
        sn_int_aprend.descricao        AS internet_aprendizagem,
        sn_int_comun.descricao         AS internet_comunidade,
        sn_lab.descricao               AS laboratorio_informatica,
        
        -- Tradução dos Indicadores de Equipamentos
        sn_desktop.descricao           AS possui_desktop_aluno,
        sn_portatil.descricao          AS possui_portatil_aluno,
        sn_tablet.descricao            AS possui_tablet_aluno,

        -- Flags numéricas (1/0)
        c.IN_INTERNET,
        c.IN_INTERNET_ALUNOS,
        c.IN_EQUIP_LOUSA_DIGITAL,
        c.IN_INTERNET_APRENDIZAGEM,
        c.IN_LABORATORIO_INFORMATICA,
        c.IN_ACESSO_INTERNET_COMPUTADOR,

        CASE WHEN c.IN_DESKTOP_ALUNO = 1 OR c.IN_COMP_PORTATIL_ALUNO = 1 OR c.IN_TABLET_ALUNO = 1 THEN 1 ELSE 0 END AS IN_DISPOSITIVO_TECNOLOGICO_ALUNO,
        -- Lógica de Perfil de Uso Tecnológico
        CASE 
            WHEN (c.IN_INTERNET_APRENDIZAGEM = 1 OR c.IN_INTERNET_ALUNOS = 1) 
                AND (c.QT_DESKTOP_ALUNO > 0 OR c.QT_COMP_PORTATIL_ALUNO > 0 OR c.QT_TABLET_ALUNO > 0 OR c.QT_EQUIP_LOUSA_DIGITAL > 0)
            THEN 'Conectividade Pedagogica Plena'

            WHEN (c.IN_INTERNET_APRENDIZAGEM = 1 OR c.IN_INTERNET_ALUNOS = 1) 
                AND (COALESCE(c.QT_DESKTOP_ALUNO, 0) + COALESCE(c.QT_COMP_PORTATIL_ALUNO, 0) + COALESCE(c.QT_TABLET_ALUNO, 0) + COALESCE(c.QT_EQUIP_LOUSA_DIGITAL, 0) = 0)
            THEN 'Conexao Sem Dispositivos'

            WHEN c.IN_INTERNET = 1 
                AND c.IN_INTERNET_APRENDIZAGEM = 0 
                AND c.IN_INTERNET_ALUNOS = 0
            THEN 'Internet Apenas Administrativa'

            WHEN c.IN_INTERNET = 0 THEN 'Sem Conectividade'

            ELSE 'Conectividade e Uso Tecnologico Indefinidos'
        END AS perfil_uso_tecnologico,

        -- Métricas Quantitativas (Todas que você listou)
        c.QT_DESKTOP_ALUNO,
        c.QT_COMP_PORTATIL_ALUNO,
        c.QT_TABLET_ALUNO,
        c.QT_EQUIP_LOUSA_DIGITAL,
        c.QT_MAT_BAS, 
        c.QT_MAT_FUND,
        c.QT_MAT_FUND_D, 
        c.QT_MAT_FUND_N,
        c.QT_MAT_MED, 
        c.QT_MAT_MED_D,
        c.QT_MAT_MED_N,
        c.QT_MAT_BAS_FEM, 
        c.QT_MAT_BAS_MASC,   
        c.QT_MAT_BAS_ND, 
        c.QT_MAT_BAS_BRANCA, 
        c.QT_MAT_BAS_PRETA, 
        c.QT_MAT_BAS_PARDA, 
        c.QT_MAT_BAS_AMARELA, 
        c.QT_MAT_BAS_INDIGENA,
        c.QT_MAT_ZR_URB, 
        c.QT_MAT_ZR_RUR,
        c.QT_DOC_BAS,
        c.QT_DOC_FUND, 
        c.QT_DOC_MED,
        c.QT_DOC_BAS_DISC_INFO_COMPUTACAO, 
        c.QT_DOC_BAS_ESPEC_EDUC_TIC

    FROM {{ ref('staging_censo_escolar') }} c
    LEFT JOIN {{ ref('labels_dependencia') }} dep ON c.TP_DEPENDENCIA = dep.codigo
    LEFT JOIN {{ ref('labels_localizacao') }} loc ON c.TP_LOCALIZACAO = loc.codigo
    LEFT JOIN {{ ref('labels_sim_nao') }} sn_int         ON c.IN_INTERNET = sn_int.codigo
    LEFT JOIN {{ ref('labels_sim_nao') }} sn_int_alu     ON c.IN_INTERNET_ALUNOS = sn_int_alu.codigo
    LEFT JOIN {{ ref('labels_sim_nao') }} sn_banda       ON c.IN_BANDA_LARGA = sn_banda.codigo
    LEFT JOIN {{ ref('labels_sim_nao') }} sn_comp        ON c.IN_COMPUTADOR = sn_comp.codigo
    LEFT JOIN {{ ref('labels_sim_nao') }} sn_acesso_comp ON c.IN_ACESSO_INTERNET_COMPUTADOR = sn_acesso_comp.codigo
    LEFT JOIN {{ ref('labels_sim_nao') }} sn_int_aprend  ON c.IN_INTERNET_APRENDIZAGEM = sn_int_aprend.codigo
    LEFT JOIN {{ ref('labels_sim_nao') }} sn_int_comun   ON c.IN_INTERNET_COMUNIDADE = sn_int_comun.codigo
    LEFT JOIN {{ ref('labels_sim_nao') }} sn_lab         ON c.IN_LABORATORIO_INFORMATICA = sn_lab.codigo
    LEFT JOIN {{ ref('labels_sim_nao') }} sn_desktop     ON c.IN_DESKTOP_ALUNO = sn_desktop.codigo
    LEFT JOIN {{ ref('labels_sim_nao') }} sn_portatil    ON c.IN_COMP_PORTATIL_ALUNO = sn_portatil.codigo
    LEFT JOIN {{ ref('labels_sim_nao') }} sn_tablet      ON c.IN_TABLET_ALUNO = sn_tablet.codigo
)

SELECT 
    *,
        -- Foco ALUNOS do Fundamental + Médio
    (COALESCE(QT_MAT_FUND, 0) + COALESCE(QT_MAT_MED, 0)) AS matricula_fund_med,

    ROUND((COALESCE(QT_MAT_FUND_D, 0) + COALESCE(QT_MAT_MED_D, 0)) * 100.0 / NULLIF((COALESCE(QT_MAT_FUND, 0) + COALESCE(QT_MAT_MED, 0)), 0), 2) AS pct_alunos_diurno,
    ROUND((COALESCE(QT_MAT_FUND_N, 0) + COALESCE(QT_MAT_MED_N, 0)) * 100.0 / NULLIF((COALESCE(QT_MAT_FUND, 0) + COALESCE(QT_MAT_MED, 0)), 0), 2) AS pct_alunos_noturno,
    ROUND((COALESCE(QT_MAT_FUND, 0) * 100.0 / NULLIF((COALESCE(QT_MAT_FUND, 0) + COALESCE(QT_MAT_MED, 0)), 0)), 2) AS pct_alunos_fund,
    ROUND((COALESCE(QT_MAT_MED, 0) * 100.0 / NULLIF((COALESCE(QT_MAT_FUND, 0) + COALESCE(QT_MAT_MED, 0)), 0)), 2) AS pct_alunos_medio,
         -- Foco DOCENTE/PROFESSOR do Fundamental + Médio
    (COALESCE(QT_DOC_MED, 0) + COALESCE(QT_DOC_FUND, 0)) AS docente_fund_med,
    -- dados de docentes são por escola, não temos a distribuição por turno, então não conseguimos calcular o percentual de docentes por turno, mas podemos calcular o percentual de docentes do fund e médio em relação ao total de docentes
    ROUND((COALESCE(QT_DOC_FUND, 0) * 100.0 / NULLIF((COALESCE(QT_DOC_MED, 0) + COALESCE(QT_DOC_FUND, 0)), 0)), 2) AS pct_docentes_fund,
    ROUND((COALESCE(QT_DOC_MED, 0) * 100.0 / NULLIF((COALESCE(QT_DOC_MED, 0) + COALESCE(QT_DOC_FUND, 0)), 0)), 2) AS pct_docentes_med,  
    -- PROPORÇÃO DE ALUNOS POR DOCENTE (Alunos do Fundamental + Médio por Docente do Fundamental + Médio)
    ROUND((COALESCE(QT_MAT_FUND, 0) + COALESCE(QT_MAT_MED, 0)) * 1.0 / NULLIF((COALESCE(QT_DOC_FUND, 0) + COALESCE(QT_DOC_MED, 0)), 0), 2) AS proporcao_alunos_por_docente,
    
    ROUND((COALESCE(QT_MAT_BAS_PRETA, 0) + COALESCE(QT_MAT_BAS_PARDA, 0)) * 100.0 / NULLIF((COALESCE(QT_MAT_BAS, 0)), 0), 2) AS pct_alunos_brasil_preta_parda,

    -- Quantidade dispositivos tecnológicos para alunos (somatório de desktop, portátil, tablet e lousa digital)
    (COALESCE(QT_DESKTOP_ALUNO, 0) + COALESCE(QT_COMP_PORTATIL_ALUNO, 0) + COALESCE(QT_TABLET_ALUNO, 0) + COALESCE(QT_EQUIP_LOUSA_DIGITAL, 0)) AS total_dispositivos_aluno,
    -- Densidade Real de PCs para o público-alvo (Alunos do Fundamental + Médio)
    ROUND(
        (COALESCE(QT_DESKTOP_ALUNO, 0) + COALESCE(QT_COMP_PORTATIL_ALUNO, 0) + COALESCE(QT_TABLET_ALUNO, 0) + COALESCE(QT_EQUIP_LOUSA_DIGITAL, 0)) * 100.0 
        / NULLIF((COALESCE(QT_MAT_FUND, 0) + COALESCE(QT_MAT_MED, 0)), 0), 2
    ) AS densidade_tecnologica_total,
    -- Densidade Real de PCs por turno (Alunos do Fundamental + Médio)
    ROUND(
        (COALESCE(QT_DESKTOP_ALUNO, 0) + COALESCE(QT_COMP_PORTATIL_ALUNO, 0) + COALESCE(QT_TABLET_ALUNO, 0) + COALESCE(QT_EQUIP_LOUSA_DIGITAL, 0)) * 100.0 
        / NULLIF((COALESCE(QT_MAT_FUND_D, 0) + COALESCE(QT_MAT_MED_D, 0)), 0), 2
    ) AS densidade_tecnologica_diurno,
    ROUND(
        (COALESCE(QT_DESKTOP_ALUNO, 0) + COALESCE(QT_COMP_PORTATIL_ALUNO, 0) + COALESCE(QT_TABLET_ALUNO, 0) + COALESCE(QT_EQUIP_LOUSA_DIGITAL, 0)) * 100.0 
        / NULLIF((COALESCE(QT_MAT_FUND_N, 0) + COALESCE(QT_MAT_MED_N, 0)), 0), 2
    ) AS densidade_tecnologica_noturno,
    -- média densidade tecnológica por turno (para comparar a densidade tecnológica entre os turnos, já que a quantidade de alunos e docentes é diferente entre eles)
    ROUND((
        ROUND(
        (COALESCE(QT_DESKTOP_ALUNO, 0) + COALESCE(QT_COMP_PORTATIL_ALUNO, 0) + COALESCE(QT_TABLET_ALUNO, 0) + COALESCE(QT_EQUIP_LOUSA_DIGITAL, 0)) * 100.0 
        / NULLIF((COALESCE(QT_MAT_FUND_D, 0) + COALESCE(QT_MAT_MED_D, 0)), 0),
        2)
        +
        ROUND(
        (COALESCE(QT_DESKTOP_ALUNO, 0) + COALESCE(QT_COMP_PORTATIL_ALUNO, 0) + COALESCE(QT_TABLET_ALUNO, 0) + COALESCE(QT_EQUIP_LOUSA_DIGITAL, 0)) * 100.0 
        / NULLIF((COALESCE(QT_MAT_FUND_N, 0) + COALESCE(QT_MAT_MED_N, 0)), 0),
        2)
    ) / 2.0, 2) AS densidade_tecnologica_media_turnos,
            -- Métricas de Apoio (Ex: Proporção de Docentes/Professores Especialistas) -- não temos a qtd de docentes com educ_tic medio + fund, por esse motivo essa proporção é em proxy escola e não turma/turno
    COALESCE(QT_DOC_BAS_ESPEC_EDUC_TIC, 0) / NULLIF(QT_DOC_BAS, 0) AS proporcao_docentes_especialista_tic
FROM dados_brutos