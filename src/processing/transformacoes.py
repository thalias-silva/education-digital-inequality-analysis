# from src.utils.database import get_duckdb_connection


# def processar_censo_escolar():
#     con = get_duckdb_connection()

#     con.execute("""
#     CREATE OR REPLACE TABLE censo_trusted AS
#     WITH escola AS (
#         SELECT 
#             CO_ENTIDADE, 
#             NU_ANO_CENSO, 
#             SG_UF, 
#             NO_MUNICIPIO,
#             TP_DEPENDENCIA, 
#             TP_LOCALIZACAO,
#             IN_INTERNET, 
#             IN_INTERNET_ALUNOS, 
#             IN_INTERNET_APRENDIZAGEM,
#             IN_INTERNET_COMUNIDADE, 
#             IN_BANDA_LARGA,
#             IN_LABORATORIO_INFORMATICA, 
#             IN_COMPUTADOR,
#             QT_DESKTOP_ALUNO, 
#             QT_COMP_PORTATIL_ALUNO, 
#             QT_TABLET_ALUNO
#         FROM read_csv_auto(
#             's3://raw/censo_escolar/2025/escola*.csv',
#             delim=';',
#             header=True,
#             encoding='latin-1'
#         )
#     ),
#     matricula AS (
#         SELECT 
#             CO_ENTIDADE,
#             QT_MAT_BAS,
#             QT_MAT_FUND,
#             QT_MAT_MED
#         FROM read_csv_auto(
#             's3://raw/censo_escolar/2025/matricula*.csv',
#             delim=';',
#             header=True,
#             encoding='latin-1'
#         )
#     ),
#     docente AS (
#         SELECT 
#             CO_ENTIDADE,
#             QT_DOC_BAS,
#             QT_DOC_INF,
#             QT_DOC_BAS_DISC_INFO_COMPUTACAO
#         FROM read_csv_auto(
#             's3://raw/censo_escolar/2025/docente*.csv',
#             delim=';',
#             header=True,
#             encoding='latin-1'
#         )
#     )
#     SELECT 
#         e.*,
#         m.QT_MAT_BAS,
#         m.QT_MAT_FUND,
#         m.QT_MAT_MED,
#         d.QT_DOC_BAS,
#         d.QT_DOC_INF,
#         d.QT_DOC_BAS_DISC_INFO_COMPUTACAO
#     FROM escola e
#     LEFT JOIN matricula m USING (CO_ENTIDADE)
#     LEFT JOIN docente d USING (CO_ENTIDADE);
#     """)

#     print("✅ Transformação finalizada!")
#     return con
from src.utils.database import get_duckdb_connection

def processar_censo_escolar():
    con = get_duckdb_connection()
    print("⏳ Iniciando transformações no DuckDB...")

    con.execute("""
    CREATE OR REPLACE TABLE censo_trusted AS
    WITH escola AS (
        SELECT CO_ENTIDADE, NU_ANO_CENSO, SG_UF, NO_MUNICIPIO, TP_DEPENDENCIA, 
               TP_LOCALIZACAO, IN_INTERNET, IN_INTERNET_ALUNOS, IN_BANDA_LARGA, IN_COMPUTADOR,
                IN_INTERNET_APRENDIZAGEM, IN_INTERNET_COMUNIDADE, IN_LABORATORIO_INFORMATICA, 
               QT_DESKTOP_ALUNO, QT_COMP_PORTATIL_ALUNO, QT_TABLET_ALUNO
        FROM read_csv_auto('s3://raw/censo_escolar/2025/escola*.csv', delim=';', header=True, encoding='latin-1')
    ),
    matricula AS (
        SELECT CO_ENTIDADE, QT_MAT_BAS, QT_MAT_FUND, QT_MAT_MED
        FROM read_csv_auto('s3://raw/censo_escolar/2025/matricula*.csv', delim=';', header=True, encoding='latin-1')
    ),
    docente AS (
        SELECT CO_ENTIDADE, QT_DOC_BAS, QT_DOC_BAS_DISC_INFO_COMPUTACAO
        FROM read_csv_auto('s3://raw/censo_escolar/2025/docente*.csv', delim=';', header=True, encoding='latin-1')
    )
    SELECT e.*, m.QT_MAT_BAS, d.QT_DOC_BAS, d.QT_DOC_BAS_DISC_INFO_COMPUTACAO
    FROM escola e
    LEFT JOIN matricula m USING (CO_ENTIDADE)
    LEFT JOIN docente d USING (CO_ENTIDADE);
    """)

    print("✅ Transformação finalizada!")
    return con