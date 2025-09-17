#!/bin/bash

set -euo pipefail

echo "🚀 [ENV-A] Subindo ambiente A com docker-compose..."

cd "$(dirname "$0")"

if ! command -v docker-compose &>/dev/null; then
  echo "❌ docker-compose não instalado. Instale antes de continuar."
  exit 1
fi

echo "🔍 Verificando se os serviços já estão rodando..."
if docker-compose ps | grep -q 'Up'; then
  echo "✅ Serviços já estão em execução."
else
  echo "📦 Iniciando os serviços do ambiente A..."
  docker-compose up -d
fi

echo "⏳ Aguardando containers ficarem saudáveis..."
SERVICES=("mlflow" "postgres" "minio")
ALL_HEALTHY=true

for SERVICE in "${SERVICES[@]}"; do
  STATUS=$(docker inspect --format='{{json .State.Health.Status}}' "env-a-${SERVICE}-1" 2>/dev/null || echo "null")
  if [[ "$STATUS" == "\"healthy\"" ]]; then
    echo "✅ $SERVICE está saudável."
  else
    echo "❌ $SERVICE não está saudável ou sem healthcheck."
    ALL_HEALTHY=false
  fi
done

if [ "$ALL_HEALTHY" = true ]; then
  echo "🎉 Todos os serviços do ambiente A estão saudáveis!"
else
  echo "⚠️ Verifique os logs: docker-compose logs"
fi