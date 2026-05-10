-- censo_traduzido
SELECT
    -- Identificação
    c.CO_ENTIDADE,
    c.NU_ANO_CENSO,
    c.SG_UF,
    c.NO_MUNICIPIO,
    c.NO_REGIAO,

    -- Tradução da Dependência (Dicionário Próprio)
    dep.descricao as dependencia_adm,
    -- Tradução da Localização
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

    -- Métricas Quantitativas
    c.QT_DESKTOP_ALUNO,
    c.QT_COMP_PORTATIL_ALUNO,
    c.QT_TABLET_ALUNO,
    c.QT_MAT_BAS, 
    c.QT_MAT_FUND, 
    c.QT_MAT_MED, 
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
    c.QT_DOC_BAS_DISC_INFO_COMPUTACAO, 
    c.QT_DOC_BAS_ESPEC_EDUC_TIC

FROM {{ ref('staging_censo_escolar') }} c
-- Join para Dependência e Localização
LEFT JOIN {{ ref('labels_dependencia') }} dep ON c.TP_DEPENDENCIA = dep.codigo
LEFT JOIN {{ ref('labels_localizacao') }} loc ON c.TP_LOCALIZACAO = loc.codigo

-- Joins de Conectividade
LEFT JOIN {{ ref('labels_sim_nao') }} sn_int         ON c.IN_INTERNET = sn_int.codigo
LEFT JOIN {{ ref('labels_sim_nao') }} sn_int_alu     ON c.IN_INTERNET_ALUNOS = sn_int_alu.codigo
LEFT JOIN {{ ref('labels_sim_nao') }} sn_banda       ON c.IN_BANDA_LARGA = sn_banda.codigo
LEFT JOIN {{ ref('labels_sim_nao') }} sn_comp        ON c.IN_COMPUTADOR = sn_comp.codigo
LEFT JOIN {{ ref('labels_sim_nao') }} sn_acesso_comp ON c.IN_ACESSO_INTERNET_COMPUTADOR = sn_acesso_comp.codigo
LEFT JOIN {{ ref('labels_sim_nao') }} sn_int_aprend  ON c.IN_INTERNET_APRENDIZAGEM = sn_int_aprend.codigo
LEFT JOIN {{ ref('labels_sim_nao') }} sn_int_comun   ON c.IN_INTERNET_COMUNIDADE = sn_int_comun.codigo
LEFT JOIN {{ ref('labels_sim_nao') }} sn_lab         ON c.IN_LABORATORIO_INFORMATICA = sn_lab.codigo

-- Joins de Equipamentos
LEFT JOIN {{ ref('labels_sim_nao') }} sn_desktop     ON c.IN_DESKTOP_ALUNO = sn_desktop.codigo
LEFT JOIN {{ ref('labels_sim_nao') }} sn_portatil    ON c.IN_COMP_PORTATIL_ALUNO = sn_portatil.codigo
LEFT JOIN {{ ref('labels_sim_nao') }} sn_tablet      ON c.IN_TABLET_ALUNO = sn_tablet.codigo