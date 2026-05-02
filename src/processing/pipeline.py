# from src.processing.transformacoes import processar_censo_escolar
# from src.processing.validacao import validar_censo

# def run_pipeline_censo():
#     con = processar_censo_escolar()
#     validar_censo(con)

#     # Exportação para a camada Trusted em Parquet
#     con.execute("COPY censo_trusted TO 's3://trusted/censo_escolar/censo_trusted.parquet' (FORMAT PARQUET);")
#     print("🚀 Pipeline concluído e arquivo salvo na camada Trusted!")
from src.processing.transformacoes import processar_censo_escolar, tratar_planilha_cetic
from src.processing.validacao import validar_censo, validar_cetic_trusted

def executar_pipeline_completo():
    """
    Orquestra a transformação e validação de todas as fontes de dados (Censo e CETIC).
    """
    print("⚙️ [PIPELINE] Iniciando processamento consolidado...")

    # --- FRENTE 1: CENSO ESCOLAR (DUCKDB) ---
    print("\n--- PROCESSANDO CENSO ESCOLAR ---")
    con = processar_censo_escolar()
    
    # Validação rigorosa do Censo
    validar_censo(con) 
    
    # Exportação final para Parquet na Trusted
    con.execute("COPY censo_trusted TO 's3://trusted/censo_escolar/censo_trusted.parquet' (FORMAT PARQUET);")
    print("🚀 Microdados do Censo salvos em Parquet na camada Trusted!")

    # --- FRENTE 2: CETIC (DOMICÍLIOS E ALUNOS) ---
    print("\n--- PROCESSANDO PLANILHAS CETIC (PANDAS) ---")
    
    config_cetic = [
        {
            "caminho": "cetic/domicilios/2025/tic_domicilios_2025_domicilios_tabela_total_v1.0.xlsx", 
            "pesquisa": "domicilios", 
            "ano": "2025"
        },
        {
            "caminho": "cetic/educacao/2024/tic_educacao_2024_alunos_tabela_total_v1.0.xlsx", 
            "pesquisa": "educacao", 
            "ano": "2024"
        }
    ]
    
    for item in config_cetic:
        # A função tratar_planilha_cetic já cuida do ffill() e do filtro de abas
        tratar_planilha_cetic(item["caminho"], item["pesquisa"], item["ano"])
        # Chama a validação específica para os arquivos gerados
        validar_cetic_trusted(item["pesquisa"], item["ano"])
    
    print("\n✅ [PIPELINE] Todas as fontes foram transformadas e validadas!")