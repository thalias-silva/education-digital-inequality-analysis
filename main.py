import sys
import os

# Garante que o Python encontre as pastas do projeto, usar apenas se rodar e não reconhecer a env
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src.ingestion.minio_client import create_buckets
from src.scraping.censo_escolar import run_pipeline as run_scraping_censo
from src.scraping.cetic import run_pipeline as run_scraping_cetic
from src.processing.pipeline import executar_pipeline_completo

def main():
    print("🚀 INICIANDO PIPELINE DE ANÁLISE DE DESIGUALDADE DIGITAL")

    # 1. INFRAESTRUTURA: Cria os buckets se não existirem
    print("\n--- ETAPA 1: INFRAESTRUTURA ---")
    create_buckets()

    # 2. INGESTÃO (SCRAPING): Busca os dados na internet e joga no MinIO
    print("\n--- ETAPA 2: INGESTÃO DE DADOS CAMADA RAW (SCRAPING) ---")
    
    try:
        print("📥 Coletando dados do Censo Escolar (INEP)...")
        run_scraping_censo()
        
        print("\n📥 Coletando dados da CETIC (TIC Domicílios e Educação)...")

        run_scraping_cetic("domicilios", "2025", "domicilios")
        run_scraping_cetic("educacao", "2024", "alunos")
        
    except Exception as e:
        print(f"⚠️ Erro durante a coleta de dados: {e}")
        print("Dica: Verifique sua conexão ou se o site do governo está instável.")
        return # Para o processo se não houver dados para processar

    # 3. TRANSFORMAÇÃO: DuckDB lê do MinIO e processa
    print("\n--- ETAPA 3: TRANSFORMAÇÃO (DUCKDB) ---")
    try:
        executar_pipeline_completo()
        print("\n✅ PIPELINE COMPLETO EXECUTADO COM SUCESSO! Verifique a camada Trusted no MinIO.")
    except Exception as e:
        print(f"❌ Erro nas transformações do DuckDB: {e}")

if __name__ == "__main__":
    main()