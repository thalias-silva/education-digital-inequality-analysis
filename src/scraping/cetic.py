import os
import requests
import zipfile
from bs4 import BeautifulSoup

from src.ingestion.minio_client import upload_file, get_s3_client

PASTA_TEMP = "data/raw/temp_cetic"
os.makedirs(PASTA_TEMP, exist_ok=True)


def buscar_link(pesquisa, ano, unidade):
    url = f"https://www.cetic.br/pt/arquivos/{pesquisa}/{ano}/{unidade}/"

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")

    for link in soup.find_all("a", href=True):
        href = link["href"]

        if href.endswith(".zip") and "xlsx" in href.lower():
            if href.startswith("/"):
                href = "https://www.cetic.br" + href
            return href

    raise Exception("❌ ZIP não encontrado")


def baixar_zip(url, nome):
    caminho = f"{PASTA_TEMP}/{nome}.zip"

    print(f"⬇️ Baixando {nome}")
    r = requests.get(url, stream=True)

    with open(caminho, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)

    return caminho


def processar_zip(caminho_zip, destino_s3, bucket):
    with zipfile.ZipFile(caminho_zip, "r") as z:
        for nome in z.namelist():
            nome_lower = nome.lower()

        if (
            "tabela_total" in nome_lower
            and "margem_de_erro" not in nome_lower
            and nome_lower.endswith(".xlsx")
        ):
                print(f"📂 Extraindo: {nome}")

                caminho_extraido = z.extract(nome, path=PASTA_TEMP)

                object_name = f"{destino_s3}/{os.path.basename(nome)}"
                upload_file(caminho_extraido, bucket, object_name)

                os.remove(caminho_extraido)


def limpar():
    for root, dirs, files in os.walk(PASTA_TEMP, topdown=False):
        for f in files:
            os.remove(os.path.join(root, f))
        for d in dirs:
            os.rmdir(os.path.join(root, d))


def run_pipeline(pesquisa, ano, unidade, bucket="raw"):
    print(f"🚀 CETIC {pesquisa} {ano}")
    # ---  LÓGICA DE VERIFICAÇÃO VALIDA DE OS ARQUIVOS JÁ EXISTEM---
    s3 = get_s3_client()
    prefixo = f"cetic/{pesquisa}/{ano}/"
    
    try:
        # Lista os objetos na pasta específica do MinIO
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefixo)
        
        # Se 'Contents' existir, significa que já há arquivos lá
        if 'Contents' in response:
            print(f"✅ Dados de {pesquisa} {ano} já existem no bucket '{bucket}'. Pulando download.")
            return # Sai da função sem rodar o resto
            
    except Exception as e:
        print(f"⚠️ Erro ao verificar MinIO: {e}. Tentando baixar por segurança.")
    # ----------------------------------

    # Se não existir, segue o fluxo normal:
    link = buscar_link(pesquisa, ano, unidade)
    zip_path = baixar_zip(link, f"{pesquisa}_{ano}")

    destino = f"cetic/{pesquisa}/{ano}"
    processar_zip(zip_path, destino, bucket)

    limpar()

    print("✅ Finalizado")


if __name__ == "__main__":
    run_pipeline("domicilios", "2025", "domicilios")
    run_pipeline("educacao", "2024", "alunos")