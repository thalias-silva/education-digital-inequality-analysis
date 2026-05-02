# from src.processing.transformacoes import processar_censo_escolar
# from src.processing.validacao import validar_censo

# def run_pipeline_censo():
#     con = processar_censo_escolar()
#     validar_censo(con)

#     con.execute("""
#     COPY censo_trusted
#     TO 's3://trusted/censo_escolar/censo_trusted.parquet'
#     (FORMAT PARQUET);
#     """)

#     print("✅ Pipeline finalizado com sucesso!")
from src.processing.transformacoes import processar_censo_escolar
from src.processing.validacao import validar_censo

def run_pipeline_censo():
    con = processar_censo_escolar()
    validar_censo(con)

    # Exportação para a camada Trusted em Parquet
    con.execute("COPY censo_trusted TO 's3://trusted/censo_escolar/censo_trusted.parquet' (FORMAT PARQUET);")
    print("🚀 Pipeline concluído e arquivo salvo na camada Trusted!")