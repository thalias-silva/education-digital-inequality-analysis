import os
import re
import zipfile
import certifi
import requests
import urllib3
from bs4 import BeautifulSoup

from src.ingestion.minio_client import upload_file

# =========================
# CONFIG
# =========================
PASTA_TEMP = "data/raw/temp_censo"
os.makedirs(PASTA_TEMP, exist_ok=True)

urllib3.disable_warnings()

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})


# =========================
# NORMALIZAÇÃO DE NOMES
# =========================
def normalizar_nome(nome_arquivo):
    nome = os.path.basename(nome_arquivo)

    # padroniza
    nome = nome.lower()

    # remove prefixos ruins do scraping
    nome = nome.replace("tabela_", "")

    # opcional: remove espaços estranhos
    nome = nome.replace(" ", "_")

    return nome


# =========================
# PEGA LINK MAIS RECENTE
# =========================
def pegar_link():
    url = "https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar"

    response = session.get(url, timeout=300)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    links = []

    for link in soup.find_all("a", href=True):
        href = link["href"]

        if "microdados_censo_escolar" in href and href.endswith(".zip"):
            match = re.search(r"(20\d{2})", href)
            if match:
                ano = int(match.group(1))
                links.append((ano, href))

    if not links:
        raise Exception("Nenhum link encontrado")

    links.sort(reverse=True)
    return links[0]


# =========================
# DOWNLOAD ZIP
# =========================
def baixar_zip(url, ano):
    caminho = f"{PASTA_TEMP}/censo_{ano}.zip"

    print(f"⬇️ Baixando {ano}")

    try:
        r = session.get(url, stream=True, timeout=60, verify=certifi.where())
    except Exception:
        print("⚠️ SSL falhou, tentando sem verificação...")
        r = session.get(url, stream=True, timeout=60, verify=False)

    r.raise_for_status()

    with open(caminho, "wb") as f:
        for chunk in r.iter_content(8192):
            if chunk:
                f.write(chunk)

    return caminho


# =========================
# EXTRAÇÃO
# =========================
def extrair_arquivos(caminho_zip):
    arquivos = []

    alvos = {
        "escola": "tabela_escola",
        "docente": "tabela_docente",
        "matricula": "tabela_matricula"
    }

    with zipfile.ZipFile(caminho_zip, "r") as z:
        for nome in z.namelist():

            nome_lower = nome.lower()

            if nome_lower.endswith(".csv"):

                for categoria, padrao in alvos.items():
                    if padrao in nome_lower:
                        print(f"📂 Extraindo [{categoria}]: {nome}")
                        caminho_extraido = z.extract(nome, path=PASTA_TEMP)
                        arquivos.append(caminho_extraido)

    return arquivos


# =========================
# UPLOAD MINIO (COM NORMALIZAÇÃO)
# =========================
def upload(arquivos, ano, bucket="raw"):
    for arq in arquivos:

        nome_limpo = normalizar_nome(arq)

        destino = f"censo_escolar/{ano}/{nome_limpo}"

        print(f"☁️ Upload: {destino}")
        upload_file(arq, bucket, destino)


# =========================
# LIMPEZA
# =========================
def limpar():
    for root, dirs, files in os.walk(PASTA_TEMP, topdown=False):
        for f in files:
            os.remove(os.path.join(root, f))
        for d in dirs:
            os.rmdir(os.path.join(root, d))


# =========================
# PIPELINE PRINCIPAL
# =========================
def run_pipeline(bucket="raw"):
    print("🚀 CENSO ESCOLAR PIPELINE")

    ano, link = pegar_link()
    print(f"📅 Ano detectado: {ano}")

    zip_path = baixar_zip(link, ano)

    arquivos = extrair_arquivos(zip_path)

    upload(arquivos, ano, bucket)

    limpar()

    print("✅ PIPELINE FINALIZADO COM SUCESSO")


# =========================
# EXECUÇÃO
# =========================
if __name__ == "__main__":
    run_pipeline()