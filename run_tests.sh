#!/usr/bin/env bash

# Ativar modo de depuração para rastrear problemas durante a execução
set -x

# Limpar cache do pip e remover pacotes problemáticos
echo "Limpando cache do pip e removendo dependências problemáticas..."
pip cache purge
pip uninstall -y numpy scipy pandas contourpy mlflow

# Instalar dependências com versões específicas
echo "Instalando dependências com versões específicas..."
pip install --upgrade \
    numpy==1.19.5 \
    pandas==1.5.3 \
    scipy==1.10.1 \
    contourpy==1.0.1 \
    mlflow==2.18.0

# Reexecutar a instalação do restante das dependências do projeto, se necessário
if [ -f "requirements.txt" ]; then
    echo "Instalando dependências do projeto listadas em requirements.txt..."
    pip install -r requirements.txt
fi

# Executar os testes com cobertura de código
echo "Executando testes com pytest..."
python3 -m pytest --cov=cd4ml --cov-report html:cov_html test

# Verificar o código com Flake8 para assegurar boas práticas
echo "Executando Flake8 para verificar o código..."
flake8 --extend-ignore T001 --max-line-length=120 cd4ml

# Finalizar com uma mensagem indicando sucesso ou falha
if [ $? -eq 0 ]; then
    echo "Todos os testes foram executados com sucesso!"
else
    echo "Falha durante a execução dos testes. Verifique os logs acima."
    exit 1
fi