# from src.utils.database import get_duckdb_connection

# def processar_censo_escolar():
#     con = get_duckdb_connection()
#     print("⏳ Iniciando transformações no DuckDB...")

#     con.execute("""
#     CREATE OR REPLACE TABLE censo_trusted AS
#     WITH escola AS (
#         SELECT CO_ENTIDADE, NU_ANO_CENSO, SG_UF, NO_MUNICIPIO, TP_DEPENDENCIA, 
#                TP_LOCALIZACAO, IN_INTERNET, IN_INTERNET_ALUNOS, IN_BANDA_LARGA, IN_COMPUTADOR,
#                 IN_INTERNET_APRENDIZAGEM, IN_INTERNET_COMUNIDADE, IN_LABORATORIO_INFORMATICA, 
#                QT_DESKTOP_ALUNO, QT_COMP_PORTATIL_ALUNO, QT_TABLET_ALUNO
#         FROM read_csv_auto('s3://raw/censo_escolar/2025/escola*.csv', delim=';', header=True, encoding='latin-1')
#     ),
#     matricula AS (
#         SELECT CO_ENTIDADE, QT_MAT_BAS, QT_MAT_FUND, QT_MAT_MED
#         FROM read_csv_auto('s3://raw/censo_escolar/2025/matricula*.csv', delim=';', header=True, encoding='latin-1')
#     ),
#     docente AS (
#         SELECT CO_ENTIDADE, QT_DOC_BAS, QT_DOC_BAS_DISC_INFO_COMPUTACAO
#         FROM read_csv_auto('s3://raw/censo_escolar/2025/docente*.csv', delim=';', header=True, encoding='latin-1')
#     )
#     SELECT e.*, m.QT_MAT_BAS, d.QT_DOC_BAS, d.QT_DOC_BAS_DISC_INFO_COMPUTACAO
#     FROM escola e
#     LEFT JOIN matricula m USING (CO_ENTIDADE)
#     LEFT JOIN docente d USING (CO_ENTIDADE);
#     """)

#     print("✅ Transformação finalizada!")
#     return con
import pandas as pd
import io
import os
import re
from src.utils.database import get_duckdb_connection
from src.ingestion.minio_client import get_s3_client, upload_file

# ==========================================
# CONFIGURAÇÕES DE FILTRO (MAPEAMENTO INTELIGENTE)
# ==========================================

# Mapeamento para TIC Domicílios: Foco em posse de equipamentos e qualidade da rede
FILTRO_DOMICILIOS = [
    "A1", "A4", "A4B", "A5", "A5A", "A6A", "A10", "A10A", "A11", "A12", "A13"
]

# Mapeamento para TIC Alunos: Foco em uso escolar, dispositivos e mediação pedagógica
FILTRO_ALUNOS = [
    "B1", "B6", "B9", "C1", "C5", "D2", "D5_1", "E1A", "E2A", "E20_1", 
    "F7", "F9", "F10", "G1", "G6", "H1", "H4A", "H4B", "H4D"
]

# ==========================================
# 1. TRANSFORMAÇÃO CENSO ESCOLAR (DUCKDB - MODO ESTÁVEL)
# ==========================================
def processar_censo_escolar():
    """
    Consolida microdados do Censo baixando arquivos localmente para evitar
    erros de cast do DuckDB (HTTPFS) em arquivos volumosos.
    """
    con = get_duckdb_connection()
    s3_client = get_s3_client()
    local_dir = "temp_censo"
    
    print(f"⏳ Iniciando transformações do Censo (Modo Local Estável)...")
    os.makedirs(local_dir, exist_ok=True)

    arquivos = {
        "escola": "escola_2025.csv",
        "matricula": "matricula_2025.csv",
        "docente": "docente_2025.csv"
    }

    try:
        # Download preventivo para evitar Internal Error de cast no DuckDB
        print("🚚 Baixando microdados da Raw para processamento local...")
        for chave, nome_arq in arquivos.items():
            s3_client.download_file('raw', f'censo_escolar/2025/{nome_arq}', f'{local_dir}/{nome_arq}')

        con.execute(f"""
        CREATE OR REPLACE TABLE censo_trusted AS
        WITH escola AS (
            SELECT CO_ENTIDADE, NU_ANO_CENSO, SG_UF, NO_MUNICIPIO, TP_DEPENDENCIA, 
                   TP_LOCALIZACAO, IN_INTERNET, IN_INTERNET_ALUNOS, IN_BANDA_LARGA, IN_COMPUTADOR,
                   IN_INTERNET_APRENDIZAGEM, IN_INTERNET_COMUNIDADE, IN_LABORATORIO_INFORMATICA, 
                   QT_DESKTOP_ALUNO, QT_COMP_PORTATIL_ALUNO, QT_TABLET_ALUNO
            FROM read_csv_auto('{local_dir}/escola_2025.csv', delim=';', header=True, encoding='latin-1')
        ),
        matricula AS (
            SELECT CO_ENTIDADE, QT_MAT_BAS, QT_MAT_FUND, QT_MAT_MED
            FROM read_csv_auto('{local_dir}/matricula_2025.csv', delim=';', header=True, encoding='latin-1')
        ),
        docente AS (
            SELECT CO_ENTIDADE, QT_DOC_BAS, QT_DOC_BAS_DISC_INFO_COMPUTACAO
            FROM read_csv_auto('{local_dir}/docente_2025.csv', delim=';', header=True, encoding='latin-1')
        )
        SELECT e.*, m.QT_MAT_BAS, d.QT_DOC_BAS, d.QT_DOC_BAS_DISC_INFO_COMPUTACAO
        FROM escola e
        LEFT JOIN matricula m USING (CO_ENTIDADE)
        LEFT JOIN docente d USING (CO_ENTIDADE);
        """)

        print("✅ Transformação do Censo finalizada com sucesso!")

    finally:
        # Limpeza obrigatória do diretório temporário
        for nome_arq in arquivos.values():
            caminho = f'{local_dir}/{nome_arq}'
            if os.path.exists(caminho):
                os.remove(caminho)
        if os.path.exists(local_dir):
            os.rmdir(local_dir)
            
    return con

# ==========================================
# 2. TRANSFORMAÇÃO CETIC (PANDAS + MINIO)
# ==========================================
def tratar_planilha_cetic(caminho_raw, pesquisa, ano):
    """
    Resolve o problema de células mescladas, filtra abas e renomeia
    tabelas extraindo o título após o hífen.
    """
    s3 = get_s3_client()
    bucket_raw = "raw"
    bucket_trusted = "trusted"
    
    filtro_atual = FILTRO_DOMICILIOS if pesquisa == "domicilios" else FILTRO_ALUNOS
    
    print(f"📡 Processando CETIC: {caminho_raw}")
    
    obj = s3.get_object(Bucket=bucket_raw, Key=caminho_raw)
    conteudo = io.BytesIO(obj['Body'].read())
    
    abas = pd.read_excel(conteudo, sheet_name=None, header=None)
    
    for nome_aba, df in abas.items():
        codigo_aba = nome_aba.strip().upper()
        
        # Filtro seletivo baseado na lista de interesse do TCC
        if not any(codigo == codigo_aba for codigo in filtro_atual):
            continue

        if df.empty or len(df.columns) < 3: 
            continue
        
        try:
            # --- TRATAMENTO DO TÍTULO (PÓS-HÍFEN) ---
            titulo_bruto = str(df.iloc[0, 0])
            tema_tabela = titulo_bruto.split(" - ", 1)[1] if " - " in titulo_bruto else titulo_bruto
            
            nome_limpo = re.sub(r'[\\/*?:"<>|]', "", tema_tabela).strip().lower()
            nome_arquivo_csv = nome_limpo.replace(" ", "_").replace(",", "")[:60] + ".csv"

            # --- ESTRUTURAÇÃO ---
            colunas_respostas = df.iloc[2, 2:].dropna().tolist()
            df.columns = ['Categoria', 'Subcategoria'] + colunas_respostas
            
            idx_total = df[df['Categoria'].astype(str).str.contains('TOTAL', na=False, case=False)].index[0]
            df_dados = df.iloc[idx_total:].reset_index(drop=True)
            
            # --- RESOLVENDO CÉLULAS MESCLADAS (FFILL) ---
            df_dados['Categoria'] = df_dados['Categoria'].ffill()
            
            # --- MELT PARA FORMATO LONG ---
            df_longo = df_dados.melt(
                id_vars=['Categoria', 'Subcategoria'],
                var_name='Indicador',
                value_name='Total'
            )
            
            # Limpeza Numérica Brasil -> Computacional
            df_longo['Total'] = pd.to_numeric(
                df_longo['Total'].astype(str).str.replace('.', '').str.replace(',', '.'), 
                errors='coerce'
            )
            df_longo = df_longo.dropna(subset=['Total'])

            # --- PERSISTÊNCIA NA TRUSTED ---
            temp_path = f"temp_{codigo_aba}.csv"
            df_longo.to_csv(temp_path, index=False, sep=";")
            
            destino_s3 = f"cetic/{pesquisa}/{ano}/{nome_arquivo_csv}"
            upload_file(temp_path, bucket_trusted, destino_s3)
            
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            print(f"✅ Aba {codigo_aba} -> {nome_arquivo_csv}")

        except Exception as e:
            print(f"⚠️ Erro na aba {nome_aba}: {e}")