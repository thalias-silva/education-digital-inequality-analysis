# def validar_censo(con):
#     print("🔍 Validando dados...")
    
#     # Validação de volume
#     total = con.execute("SELECT COUNT(*) FROM censo_trusted").fetchone()[0]
#     if total == 0: raise Exception("❌ Tabela vazia!")
    
#     # Validação de duplicidade
#     duplicados = con.execute("SELECT COUNT(*) FROM (SELECT CO_ENTIDADE FROM censo_trusted GROUP BY 1 HAVING COUNT(*) > 1)").fetchone()[0]
#     if duplicados > 0: print(f"⚠️ Atenção: {duplicados} duplicatas encontradas.")
    
#     print(f"🎯 Sucesso! {total} registros validados.")
import pandas as pd
import os

# ==========================================
# 1. VALIDAÇÃO CENSO ESCOLAR (DUCKDB)
# ==========================================
def validar_censo(con):
    """
    Valida a integridade dos microdados processados pelo DuckDB.
    """
    print("🔍 [VALIDAÇÃO] Checando dados do Censo...")
    
    # Validação de volume
    total = con.execute("SELECT COUNT(*) FROM censo_trusted").fetchone()[0]
    if total == 0: 
        raise Exception("❌ ERRO CRÍTICO: Tabela censo_trusted está vazia!")
    
    # Validação de duplicidade (Chave primária CO_ENTIDADE)
    duplicados = con.execute("""
        SELECT COUNT(*) 
        FROM (SELECT CO_ENTIDADE FROM censo_trusted GROUP BY 1 HAVING COUNT(*) > 1)
    """).fetchone()[0]
    
    if duplicados > 0: 
        print(f"⚠️ ATENÇÃO: {duplicados} entidades duplicadas encontradas no Censo.")
    
    print(f"🎯 SUCESSO: {total} registros de escolas validados no Censo.")

# ==========================================
# 2. VALIDAÇÃO CETIC (PANDAS/CSV)
# ==========================================
def validar_cetic_trusted(pesquisa, ano):
    """
    Valida se as abas filtradas da CETIC foram geradas corretamente na camada Trusted.
    """
    print(f"🔍 [VALIDAÇÃO] Checando arquivos Trusted da CETIC ({pesquisa} {ano})...")
    
    # Como o processamento salva arquivos temporários ou via S3, 
    # podemos validar se as tabelas processadas possuem os campos obrigatórios
    # Aqui, você pode checar se a estrutura Long (Tidy) foi respeitada.
    
    # Dica de Business Analyst: 
    # Em um ambiente de produção, você poderia baixar uma amostra 
    # da Trusted para garantir que não há valores nulos na coluna 'Total'.
    pass

def verificar_limpeza_mesclagem(df, nome_tabela):
    """
    Valida se o ffill() funcionou: não deve haver 'Categoria' vazia.
    """
    nulos_categoria = df['Categoria'].isnull().sum()
    if nulos_categoria > 0:
        print(f"⚠️ ATENÇÃO: A tabela '{nome_tabela}' possui {nulos_categoria} linhas sem categoria. Verifique a mesclagem.")
    else:
        print(f"✔️ Tabela '{nome_tabela}': Células mescladas resolvidas com sucesso.")