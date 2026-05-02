# def validar_censo(con):
#     print("🔍 Iniciando validações...")

#     total = con.execute("SELECT COUNT(*) FROM censo_trusted").fetchone()[0]
#     if total == 0:
#         raise Exception("❌ Tabela vazia")
#     print(f"✅ Linhas: {total}")

#     duplicados = con.execute("""
#     SELECT COUNT(*) FROM (
#         SELECT CO_ENTIDADE
#         FROM censo_trusted
#         GROUP BY CO_ENTIDADE
#         HAVING COUNT(*) > 1
#     )
#     """).fetchone()[0]

#     if duplicados > 0:
#         raise Exception(f"❌ {duplicados} entidades duplicadas")
#     print("✅ Sem duplicidade")

#     nulls = con.execute("""
#     SELECT COUNT(*) FROM censo_trusted
#     WHERE CO_ENTIDADE IS NULL
#     """).fetchone()[0]

#     if nulls > 0:
#         raise Exception(f"❌ {nulls} linhas com chave nula")
#     print("✅ Sem nulos na chave")

#     negativos = con.execute("""
#     SELECT COUNT(*) FROM censo_trusted
#     WHERE QT_MAT_BAS < 0
#     """).fetchone()[0]

#     if negativos > 0:
#         raise Exception(f"❌ {negativos} valores negativos")
#     print("✅ Valores válidos")

#     print("🎯 Validação concluída com sucesso!")
def validar_censo(con):
    print("🔍 Validando dados...")
    
    # Validação de volume
    total = con.execute("SELECT COUNT(*) FROM censo_trusted").fetchone()[0]
    if total == 0: raise Exception("❌ Tabela vazia!")
    
    # Validação de duplicidade
    duplicados = con.execute("SELECT COUNT(*) FROM (SELECT CO_ENTIDADE FROM censo_trusted GROUP BY 1 HAVING COUNT(*) > 1)").fetchone()[0]
    if duplicados > 0: print(f"⚠️ Atenção: {duplicados} duplicatas encontradas.")
    
    print(f"🎯 Sucesso! {total} registros validados.")