#!/usr/bin/env bash

set -e  # Pare em caso de erro
set -x  # Ative o modo de depuração para rastreamento

echo "Executando testes no container Docker..."

echo "Limpando possíveis caches antigos..."
pip cache purge

echo "Instalando dependências específicas..."
pip install numpy==1.21.6 pandas==1.3.5 scipy==1.7.3 mlflow==1.23.1 pytest pytest-cov flake8

if [ -f "requirements.txt" ]; then
    echo "Instalando dependências adicionais do requirements.txt..."
    pip install -r requirements.txt
fi

echo "Executando testes com pytest..."
python3 -m pytest --cov=cd4ml.problems.rendimento --cov-report html:cov_html tests/rendimento

if [ $? -eq 0 ]; then
    echo "Testes executados com sucesso!"
else
    echo "Falha durante os testes. Verifique os logs acima."
    exit 1
fi

echo "Verificando estilo de código com Flake8..."
flake8 --extend-ignore T001 --max-line-length=120 cd4ml/problems/rendimento