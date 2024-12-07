#!/usr/bin/env bash
export PYTHONWARNINGS="ignore:numpy"

# Garantir dependências compatíveis
pip install --upgrade mlflow numpy<1.20

# Comando para executar os testes
command="python3 -m pytest --cov=cd4ml --cov-report html:cov_html test"

echo "$command"
eval "$command"

echo
echo Flake8 comments:
# extend-ignore T001 ignora print() statements
flake8 --extend-ignore T001 --max-line-length=120 cd4ml