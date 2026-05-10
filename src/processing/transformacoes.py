import pandas as pd
import io
import os
import re

from openpyxl import load_workbook
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
            SELECT CO_ENTIDADE, NU_ANO_CENSO, SG_UF, NO_MUNICIPIO, NO_REGIAO, TP_DEPENDENCIA, 
                   TP_LOCALIZACAO, IN_INTERNET, IN_INTERNET_ALUNOS, IN_BANDA_LARGA, IN_COMPUTADOR,
                   IN_ACESSO_INTERNET_COMPUTADOR, IN_INTERNET_APRENDIZAGEM, IN_INTERNET_COMUNIDADE, 
                   IN_LABORATORIO_INFORMATICA, IN_DESKTOP_ALUNO,QT_DESKTOP_ALUNO,
                    IN_COMP_PORTATIL_ALUNO, QT_COMP_PORTATIL_ALUNO,IN_TABLET_ALUNO,QT_TABLET_ALUNO,
            FROM read_csv_auto('{local_dir}/escola_2025.csv', delim=';', header=True, encoding='latin-1')
        ),
        matricula AS (
            SELECT CO_ENTIDADE, QT_MAT_BAS, QT_MAT_FUND, QT_MAT_MED, QT_MAT_BAS_FEM, QT_MAT_BAS_MASC,   
            QT_MAT_BAS_ND, QT_MAT_BAS_BRANCA, QT_MAT_BAS_PRETA, QT_MAT_BAS_PARDA, QT_MAT_BAS_AMARELA, 
            QT_MAT_BAS_INDIGENA, QT_MAT_ZR_URB, QT_MAT_ZR_RUR
            FROM read_csv_auto('{local_dir}/matricula_2025.csv', delim=';', header=True, encoding='latin-1')
        ),
        docente AS (
            SELECT CO_ENTIDADE, QT_DOC_BAS, QT_DOC_BAS_DISC_INFO_COMPUTACAO, QT_DOC_BAS_ESPEC_EDUC_TIC
            FROM read_csv_auto('{local_dir}/docente_2025.csv', delim=';', header=True, encoding='latin-1')
        )
        SELECT e.*, m.* EXCLUDE (CO_ENTIDADE), d.* EXCLUDE (CO_ENTIDADE) 
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
    import io
    import os
    import re
    import pandas as pd

    s3 = get_s3_client()
    bucket_raw = "raw"
    bucket_refined = "refined"

    bucket_trusted = "trusted"

    filtro_atual = FILTRO_DOMICILIOS if pesquisa == "domicilios" else FILTRO_ALUNOS

    print(f"📡 Processando CETIC: {caminho_raw}")

    obj = s3.get_object(Bucket=bucket_raw, Key=caminho_raw)
    conteudo = io.BytesIO(obj["Body"].read())

    abas = pd.read_excel(
        conteudo,
        sheet_name=None,
        header=None,
        engine="openpyxl"
    )

    for nome_aba, df in abas.items():
        codigo_aba = str(nome_aba).strip().upper()

        if codigo_aba not in filtro_atual:
            continue

        if df.empty or df.shape[1] < 3:
            print(f"⚠️ Aba {nome_aba} ignorada: estrutura insuficiente.")
            continue

        try:
            df = df.copy()

            df.iloc[:, 0] = df.iloc[:, 0].ffill()
            if df.shape[1] > 1:
                df.iloc[:, 1] = df.iloc[:, 1].ffill()

            titulo_bruto = str(df.iloc[0, 0]).strip()
            tema_tabela = titulo_bruto.split(" - ", 1)[1] if " - " in titulo_bruto else titulo_bruto

            nome_limpo = re.sub(r'[\\/*?:"<>|]', "", tema_tabela).strip().lower()
            nome_limpo = re.sub(r"\s+", "_", nome_limpo)
            nome_limpo = nome_limpo.replace(",", "").replace(";", "")
            nome_base = f"{codigo_aba.lower()}_{nome_limpo[:80]}"

            header_idx = 2
            if len(df) <= header_idx:
                print(f"⚠️ Aba {nome_aba} ignorada: sem cabeçalho esperado.")
                continue

            cabecalho = df.iloc[header_idx].tolist()
            colunas = ["Categoria", "Subcategoria"] + [
                str(x).strip() if pd.notna(x) else f"col_{i}"
                for i, x in enumerate(cabecalho[2:], start=3)
            ]

            df_dados = df.iloc[header_idx + 1:].reset_index(drop=True).copy()

            if df_dados.shape[1] < len(colunas):
                for _ in range(len(colunas) - df_dados.shape[1]):
                    df_dados[df_dados.shape[1]] = None

            df_dados = df_dados.iloc[:, :len(colunas)]
            df_dados.columns = colunas
            df_dados = df_dados.dropna(how="all")

            df_dados["Categoria"] = df_dados["Categoria"].ffill()
            df_dados["Subcategoria"] = df_dados["Subcategoria"].ffill()

            df_dados = df_dados[
                ~df_dados["Categoria"].astype(str).str.contains("Fonte:", case=False, na=False)
            ]

            colunas_valor = [c for c in df_dados.columns if c not in ["Categoria", "Subcategoria"]]
            df_dados = df_dados.dropna(subset=colunas_valor, how="all")

            df_longo = df_dados.melt(
                id_vars=["Categoria", "Subcategoria"],
                var_name="Indicador",
                value_name="Total"
            )

            for col in ["Categoria", "Subcategoria", "Indicador"]:
                df_longo[col] = df_longo[col].astype(str).str.strip()

            df_longo["Total"] = (
                df_longo["Total"]
                .astype(str)
                .str.strip()
                .str.replace(".", "", regex=False)
                .str.replace(",", ".", regex=False)
            )
            df_longo["Total"] = pd.to_numeric(df_longo["Total"], errors="coerce")
            df_longo = df_longo.dropna(subset=["Total"])

            temp_csv = f"temp_{nome_base}.csv"
            temp_parquet = f"temp_{nome_base}.parquet"

            df_longo.to_csv(temp_csv, index=False, sep=";", encoding="utf-8-sig")
            df_longo.to_parquet(temp_parquet, index=False)

            destino_csv = f"cetic/{pesquisa}/{ano}/{nome_base}.csv"
            destino_parquet = f"cetic/{pesquisa}/{ano}/{nome_base}.parquet"

            upload_file(temp_csv, bucket_trusted, destino_csv)
            upload_file(temp_parquet, bucket_trusted, destino_parquet)

            if os.path.exists(temp_csv):
                os.remove(temp_csv)
            if os.path.exists(temp_parquet):
                os.remove(temp_parquet)

            print(f"✅ Aba {codigo_aba} processada: {nome_base}")

        except Exception as e:
            print(f"⚠️ Erro na aba {nome_aba}: {e}")
