WITH 
calculo_metricas AS (
    SELECT *,
        -- Foco ALUNOS do Fundamental + Médio
        (COALESCE(QT_MAT_FUND, 0) + COALESCE(QT_MAT_MED, 0)) AS matricula_fund_med,
        -- Foco DOCENTE/PROFESSOR do Fundamental + Médio
        (COALESCE(QT_DOC_MED, 0) + COALESCE(QT_DOC_FUND, 0)) AS docente_fund_med,
    /*PILAR 2: DENSIDADE DE DISPOSITIVOS
            Somamos os 3 tipos de equipamentos e dividimos pelo total de matriculas
            Usamos COALESCE para garantir que valores nulos sejam tratados como 0, e NULLIF na divisao para evitar erro de divisao por zero*/
        (COALESCE(QT_DESKTOP_ALUNO, 0) + COALESCE(QT_COMP_PORTATIL_ALUNO, 0) + COALESCE(QT_TABLET_ALUNO, 0)) / NULLIF((COALESCE(QT_MAT_FUND, 0) + COALESCE(QT_MAT_MED, 0)), 0) AS densidade_pcs_total,
        -- Percentual de Alunos por Turno (Base: Fundamental + Médio)
        (COALESCE(QT_MAT_FUND_D, 0) + COALESCE(QT_MAT_MED_D, 0)) / NULLIF((COALESCE(QT_MAT_FUND, 0) + COALESCE(QT_MAT_MED, 0)), 0) AS pct_alunos_diurno,
        (COALESCE(QT_MAT_FUND_N, 0) + COALESCE(QT_MAT_MED_N, 0)) / NULLIF((COALESCE(QT_MAT_FUND, 0) + COALESCE(QT_MAT_MED, 0)), 0) AS pct_alunos_noturno,
        -- Densidade Real de PCs para o público-alvo
        ROUND((COALESCE(QT_DESKTOP_ALUNO, 0) + COALESCE(QT_COMP_PORTATIL_ALUNO, 0) + COALESCE(QT_TABLET_ALUNO, 0) + COALESCE(QT_EQUIP_LOUSA_DIGITAL, 0)) 
            / NULLIF((COALESCE(QT_MAT_FUND, 0) + COALESCE(QT_MAT_MED, 0)), 0), 2) AS densidade_tecnologica_total,
        -- Métricas de Apoio (Ex: Proporção de Docentes/Professores Especialistas) -- não temos a qtd de docentes com educ_tic medio + fund, por esse motivo essa proporção é em proxy escola e não turma/turno
        COALESCE(QT_DOC_BAS_ESPEC_EDUC_TIC, 0) / NULLIF(QT_DOC_BAS, 0) AS proporcao_docentes_especialista_tic
    FROM {{ ref('refined_censo_escolar') }}
)
    SELECT *
    FROM calculo_metricas