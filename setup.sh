#!/bin/bash

# garante que estamos na raiz do projeto
cd "$(dirname "$0")"

# verifica se venv existe
if [ ! -d "venv" ]; then
  echo "📦 venv não encontrado. Criando..."
  python3 -m venv venv
else
  echo "📦 venv já existe. Usando o existente."
fi

# ativa venv
source venv/bin/activate

# atualiza pip dentro do venv
python -m pip install --upgrade pip

# instala dependências
pip install -r requirements.txt

echo "✅ Ambiente pronto!"
echo "Para ativar depois: source venv/bin/activate"