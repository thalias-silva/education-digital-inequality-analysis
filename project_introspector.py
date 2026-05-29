import os
import json


# =========================
# CONFIGURAÇÕES
# =========================

IGNORE_DIRS = {
    "venv", "__pycache__", ".git", "target",
    "dbt_packages", ".ipynb_checkpoints",
    ".vscode", "logs"
}

IGNORE_FILES = {".DS_Store"}


# =========================
# LEITURA DE CONTEÚDO
# =========================

def read_file_sample(path):
    """Lê uma amostra do arquivo para análise leve de conteúdo"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read(2000)
    except:
        return ""


def extract_py_doc(file_path):
    """Extrai docstring do módulo Python"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        if '"""' in content:
            start = content.find('"""') + 3
            end = content.find('"""', start)
            return content[start:end].strip()

    except:
        pass

    return None


# =========================
# CLASSIFICAÇÃO INTELIGENTE
# =========================

def detect_domain(file_name, content=""):
    """
    Detecta camada de arquitetura do projeto
    baseado no nome do arquivo + conteúdo
    """

    text = (file_name + " " + content).lower()

    # ingestion / scraping
    if any(x in text for x in ["scraping", "requests", "beautifulsoup", "download", "url"]):
        return "ingestion / scraping"

    # storage / ingestion
    if any(x in text for x in ["minio", "upload", "bucket", "s3"]):
        return "storage / ingestion"

    # processing layer
    if any(x in text for x in ["transform", "validacao", "clean", "pipeline"]):
        return "processing layer"

    # dbt layer
    # dbt (SÓ quando for estruturalmente dbt de verdade)
    if "/models/" in content or "models/" in content:
        
        if "staging" in content:
            return "dbt - staging layer"
        
        if "refined" in content:
            return "dbt - refined layer"
        
        return "dbt transformation"

    # analytics
    if file_name.endswith(".ipynb") or "notebook" in file_name:
        return "analytics / exploration"

    return "other"


def classify_file(file_name):
    """Classifica tipo básico do arquivo"""
    if file_name.endswith(".py"):
        return "python"
    if file_name.endswith(".sql"):
        return "dbt_model"
    if file_name.endswith(".ipynb"):
        return "notebook"
    if file_name.endswith(".md"):
        return "documentation"
    return "file"


# =========================
# SCANNER DO PROJETO
# =========================

def scan_project(base_path="."):
    project = {}

    for root, dirs, files in os.walk(base_path):

        # remove diretórios ignorados
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        rel_path = os.path.relpath(root, base_path)

        if rel_path == ".":
            rel_path = "root"

        project[rel_path] = []

        for file in files:
            if file in IGNORE_FILES:
                continue

            file_path = os.path.join(root, file)

            # =========================
            # ANALISAR CONTEÚDO
            # =========================
            content = ""
            docstring = None

            if file.endswith(".py"):
                content = read_file_sample(file_path)
                docstring = extract_py_doc(file_path)

            # =========================
            # CRIAR ENTRADA INTELIGENTE
            # =========================
            entry = {
                "name": file,
                "type": classify_file(file),
                "path": file_path,
                "docstring": docstring,
                "content_insight": detect_domain(file, file_path + " " + content)
            }

            project[rel_path].append(entry)

    return project


# =========================
# EXECUÇÃO
# =========================

if __name__ == "__main__":
    project_map = scan_project(".")

    with open("project_map.json", "w", encoding="utf-8") as f:
        json.dump(project_map, f, indent=2, ensure_ascii=False)

    print("✅ project_map.json gerado com sucesso!")