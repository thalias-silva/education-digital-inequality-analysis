import json

def generate_readme(data):
    md = "# 📊 Documentação do Projeto\n\n"
    md += "Projeto de análise de exclusão digital usando Censo Escolar + CETIC + DBT\n\n"

    for folder, files in data.items():
        md += f"## 📁 {folder}\n\n"

        for f in files:
            md += f"### {f['name']}\n"

            md += f"- Tipo: {f.get('type')}\n"

            # 🔥 NOVO: camada de arquitetura
            if f.get("content_insight"):
                md += f"- Camada: {f['content_insight']}\n"

            # 🔥 NOVO: docstring (se existir)
            if f.get("docstring"):
                md += f"- Descrição: {f['docstring']}\n"

            md += "\n"

    return md


if __name__ == "__main__":
    with open("project_map.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    readme = generate_readme(data)

    with open("README_AUTOMATICO.md", "w", encoding="utf-8") as f:
        f.write(readme)

    print("✅ README_AUTOMATICO.md gerado com sucesso!")