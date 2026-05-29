import json


def build_pipeline(map_data):
    stages = {}

    for folder, files in map_data.items():
        for f in files:
            stage = f.get("content_insight", "other")
            name = f["name"]

            if stage not in stages:
                stages[stage] = []

            stages[stage].append(name)

    return stages

def render_mermaid(stages):
    diagram = ["flowchart LR"]

    # =========================
    # SOURCES (ORIGENS DOS DADOS)
    # =========================
    diagram.append('CENSO["📊 Censo Escolar (INEP)"]')
    diagram.append('CETIC["🌐 CETIC TIC Educação/Domicílios"]')

    # =========================
    # INGESTION & PROCESSING (PYTHON + DUCKDB)
    # =========================
    diagram.append('SCRAPE["⚙️ Python Scrapers / Ingestion"]')
    diagram.append('PROC["🧹 Processamento & Validação (transformacoes.py)"]')

    # =========================
    # DATA LAKE (MINIO BUCKETS)
    # =========================
    diagram.append('RAW["🟤 Data Lake - Camada Raw (MinIO)"]')
    diagram.append('TRUSTED["⚪ Data Lake - Camada Trusted (Parquet / MinIO)"]')

    # =========================
    # DBT - STAGING LAYER (VIEWS)
    # =========================
    diagram.append('STG_CENSO["staging_censo_escolar"]')
    diagram.append('STG_CETIC["staging_cetic"]')

    # =========================
    # DBT - REFINED LAYER (TABLES / MARTS)
    # =========================
    diagram.append('REF_CENSO["refined_censo_escolar"]')
    diagram.append('REF_SMED["refined_censo_smed_regiao"]')
    diagram.append('REF_VULN["refined_censo_vulnerabilidade"]')
    diagram.append('REF_COV["refined_indicadores_cobertura"]')

    # =========================
    # ANALYTICS / CONSUMPTION
    # =========================
    diagram.append('ANL["📈 Analytics / Notebooks (PCA, EDA)"]')

    # =========================
    # PIPELINE FLOWS (FRENTE PYTHON)
    # =========================
    diagram.append("CENSO --> SCRAPE")
    diagram.append("CETIC --> SCRAPE")
    diagram.append("SCRAPE --> RAW")
    diagram.append("RAW --> PROC")
    diagram.append("PROC --> TRUSTED")
    
    # O dbt consome os Parquets da Trusted
    diagram.append("TRUSTED --> STG_CENSO")
    diagram.append("TRUSTED --> STG_CETIC")

    # =========================
    # DBT INTERNAL LINEAGE (LINHAGEM DOS MODELOS)
    # =========================
    # Modelos refinados que dependem do Censo de Staging
    diagram.append("STG_CENSO --> REF_CENSO")
    diagram.append("STG_CENSO --> REF_SMED")
    diagram.append("STG_CENSO --> REF_VULN")
    
    # Modelo de cobertura cruza dados das duas fontes (Censo e CETIC)
    diagram.append("STG_CENSO --> REF_COV")
    diagram.append("STG_CETIC --> REF_COV")

    # Entrega final para a camada de Analytics
    diagram.append("REF_CENSO --> ANL")
    diagram.append("REF_SMED --> ANL")
    diagram.append("REF_VULN --> ANL")
    diagram.append("REF_COV --> ANL")

    # =========================
    # STYLES (MDS / AWS PALETTE)
    # =========================
    diagram.append("classDef source fill:#e3f2fd,stroke:#1565c0")
    diagram.append("classDef Python fill:#ede7f6,stroke:#512da8")
    diagram.append("classDef lake fill:#e0f7fa,stroke:#006064")
    diagram.append("classDef dbtStg fill:#fff3e0,stroke:#ffb74d")
    diagram.append("classDef dbtRef fill:#ffe0b2,stroke:#f57c00")
    diagram.append("classDef analytics fill:#e8f5e9,stroke:#2e7d32")

    diagram.append("class CENSO,CETIC source")
    diagram.append("class SCRAPE,PROC Python")
    diagram.append("class RAW,TRUSTED lake")
    diagram.append("class STG_CENSO,STG_CETIC dbtStg")
    diagram.append("class REF_CENSO,REF_SMED,REF_VULN,REF_COV dbtRef")
    diagram.append("class ANL analytics")

    return "\n".join(diagram)
# def render_mermaid(stages):
#     diagram = ["flowchart LR"]

#     # =========================
#     # SOURCES
#     # =========================
#     diagram.append('CENSO["Censo Escolar (INEP)"]')
#     diagram.append('CETIC["CETIC TIC Educação/Domicílios"]')

#     # =========================
#     # INGESTION
#     # =========================
#     diagram.append('ING["Ingestion Layer (Python Scrapers)"]')

#     # =========================
#     # STORAGE (DATA LAKE)
#     # =========================
#     diagram.append('RAW["Data Lake Raw (MinIO / DuckDB)"]')

#     # =========================
#     # PROCESSING
#     # =========================
#     diagram.append('PROC["Processing Layer (transformacoes.py)"]')

#     # =========================
#     # DBT
#     # =========================
#     diagram.append('STG["DBT Staging Layer"]')
#     diagram.append('REF["DBT Refined Layer"]')

#     # =========================
#     # ANALYTICS
#     # =========================
#     diagram.append('ANL["Analytics / Notebooks (PCA, EDA)"]')

#     # =========================
#     # FLOWS
#     # =========================
#     diagram.append("CENSO --> ING")
#     diagram.append("CETIC --> ING")
#     diagram.append("ING --> RAW")
#     diagram.append("RAW --> PROC")
#     diagram.append("PROC --> STG")
#     diagram.append("STG --> REF")
#     diagram.append("REF --> ANL")
#     diagram.append("classDef source fill:#e1f5fe,stroke:#0288d1")
#     diagram.append("classDef storage fill:#ede7f6,stroke:#5e35b1")
#     diagram.append("classDef process fill:#fff3e0,stroke:#fb8c00")
#     diagram.append("classDef analytics fill:#e8f5e9,stroke:#43a047")
#     diagram.append("class CENSO,CETIC source")
#     diagram.append("class RAW storage")
#     diagram.append("class PROC,STG,REF process")
#     diagram.append("class ANL analytics")
#     return "\n".join(diagram)

if __name__ == "__main__":
    with open("project_map.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    stages = build_pipeline(data)
    diagram = render_mermaid(stages)

    with open("pipeline_diagram.md", "w", encoding="utf-8") as f:
        f.write("## 📊 Pipeline do Projeto\n\n")
        f.write("```mermaid\n")
        f.write(diagram)
        f.write("\n```")

    print("✅ pipeline_diagram.md gerado com sucesso!")