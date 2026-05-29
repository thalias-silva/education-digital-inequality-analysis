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
    # SOURCES
    # =========================
    diagram.append('CENSO["📊 Censo Escolar (INEP)"]')
    diagram.append('CETIC["🌐 CETIC TIC Educação/Domicílios"]')

    # =========================
    # INGESTION (GLUE / SCRAPING)
    # =========================
    diagram.append('GLUE["⚙️ AWS Glue / Python Scrapers"]')
    diagram.append('VALID["🔍 Validação & Tratamento Inicial"]')

    # =========================
    # DATA LAKE (S3 STYLE)
    # =========================
    diagram.append('BRONZE["🟤 Data Lake - Bronze (Raw / MinIO)"]')
    diagram.append('SILVER["⚪ Data Lake - Silver (Cleaned / DuckDB)"]')

    # =========================
    # DBT LAYER
    # =========================
    diagram.append('DBT_STG["🟡 dbt Staging Models"]')
    diagram.append('DBT_REF["🟠 dbt Refined Models"]')

    # =========================
    # LINEAGE EXEMPLO (DBT REAL)
    # =========================
    diagram.append('STG_CENSO["staging_censo_escolar"]')
    diagram.append('STG_CETIC["staging_cetic"]')
    diagram.append('REF_EX["refined_indicadores_cobertura"]')

    # =========================
    # ANALYTICS
    # =========================
    diagram.append('ANL["📈 Analytics / Notebooks (PCA, EDA)"]')

    # =========================
    # FLOWS (DATA PLATFORM)
    # =========================
    diagram.append("CENSO --> GLUE")
    diagram.append("CETIC --> GLUE")
    diagram.append("GLUE --> VALID")
    diagram.append("VALID --> BRONZE")
    diagram.append("BRONZE --> SILVER")
    diagram.append("SILVER --> DBT_STG")
    diagram.append("DBT_STG --> DBT_REF")
    diagram.append("DBT_REF --> ANL")

    # =========================
    # DBT LINEAGE (IMPORTANTE!)
    # =========================
    diagram.append("DBT_STG --> STG_CENSO")
    diagram.append("DBT_STG --> STG_CETIC")
    diagram.append("STG_CENSO --> REF_EX")
    diagram.append("STG_CETIC --> REF_EX")

    # =========================
    # STYLES (AWS STYLE)
    # =========================
    diagram.append("classDef source fill:#e3f2fd,stroke:#1565c0")
    diagram.append("classDef glue fill:#ede7f6,stroke:#512da8")
    diagram.append("classDef lake fill:#e0f7fa,stroke:#006064")
    diagram.append("classDef dbt fill:#fff3e0,stroke:#ef6c00")
    diagram.append("classDef analytics fill:#e8f5e9,stroke:#2e7d32")

    diagram.append("class CENSO,CETIC source")
    diagram.append("class GLUE,VALID glue")
    diagram.append("class BRONZE,SILVER lake")
    diagram.append("class DBT_STG,DBT_REF,STG_CENSO,STG_CETIC,REF_EX dbt")
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