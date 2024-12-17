#!/usr/bin/env bash

set -e  # Pare em caso de erro
set -x  # Ative o modo de depuração para rastreamento

echo "Executando no container Docker..."

# Definir cache do pip
CACHE_DIR="/tmp/pip-cache"

echo "Configurando diretório de cache: $CACHE_DIR"
mkdir -p "$CACHE_DIR"

# Instalação com retries
retry_count=3
for i in $(seq 1 $retry_count); do
    echo "Tentativa $i de instalação de dependências..."

    pip install --index-url https://pypi.org/simple \
                --trusted-host pypi.org \
                --trusted-host files.pythonhosted.org \
                --cache-dir="$CACHE_DIR" \
                --default-timeout=300 \
                --upgrade mlflow "numpy<1.20" && break

    echo "Falha na tentativa $i. Aguardando 30 segundos antes de tentar novamente..."
    sleep 30
done

# Instala dependências do requirements.txt, se existir
if [ -f "requirements.txt" ]; then
    echo "Instalando dependências do requirements.txt..."
    pip install --cache-dir="$CACHE_DIR" --default-timeout=300 -r requirements.txt
fi

echo "Executando testes com pytest..."
python3 -m pytest --cov=cd4ml --cov-report html:cov_html test || {
    echo "Falha nos testes. Verifique os logs acima."
    exit 1
}

echo "Executando verificação com Flake8..."
flake8 --extend-ignore T001 --max-line-length=120 cd4ml

echo "Script concluído com sucesso!"