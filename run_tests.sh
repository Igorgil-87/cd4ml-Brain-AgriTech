#!/bin/bash
set -e  # Termina o script em caso de erro

echo "=== Criando ambiente virtual ==="
python3 -m venv test_env

echo "=== Ativando ambiente virtual ==="
source test_env/bin/activate

VENV_PYTHON="$(pwd)/test_env/bin/python"
LOG_FILE="test_execution.log"
CACHE_DIR="/tmp/pip-cache"
RETRY_COUNT=3
TEST_DIR="cd4ml/problems/rendimento/tests"

echo "=== Configurando cache: ${CACHE_DIR} ==="
mkdir -p ${CACHE_DIR}

echo "=== Instalando dependências específicas com retry ==="
for i in $(seq 1 ${RETRY_COUNT}); do
    ${VENV_PYTHON} -m pip install --upgrade pip > ${LOG_FILE} 2>&1
    ${VENV_PYTHON} -m pip install --cache-dir=${CACHE_DIR} numpy>=1.22.0,<1.26.0 pandas>=1.5.0,<1.6.0 mlflow==2.1.1 scipy>=1.9.0,<1.11.0 pytest==7.2.1 requests-mock==1.10.0 >> ${LOG_FILE} 2>&1
    if [ $? -eq 0 ]; then
        echo "Instalação concluída com sucesso!"
        break
    fi
    echo "Tentativa ${i} falhou. Retentando..."
    if [ $i -eq ${RETRY_COUNT} ]; then
        echo "Falha na instalação após ${RETRY_COUNT} tentativas."
        cat ${LOG_FILE}
        exit 1
    fi
done

echo "=== Listando pacotes instalados ==="
${VENV_PYTHON} -m pip freeze >> ${LOG_FILE}

echo "=== Executando testes com pytest ==="
${VENV_PYTHON} -m pytest ${TEST_DIR} --maxfail=2 --disable-warnings --tb=short | tee -a ${LOG_FILE}

echo "=== Desativando e removendo ambiente virtual ==="
deactivate
rm -rf test_env

echo "=== Testes concluídos com sucesso! ==="