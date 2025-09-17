#!/bin/bash
echo "🔍 Verificando saúde dos serviços do ambiente A..."

SERVICES=("mlflow" "postgres" "minio")
ALL_HEALTHY=true

for SERVICE in "${SERVICES[@]}"; do
  CONTAINER_ID=$(docker-compose -f docker-compose.yaml ps -q "$SERVICE")
  
  if [ -z "$CONTAINER_ID" ]; then
    echo "❌ Serviço $SERVICE não encontrado."
    ALL_HEALTHY=false
    continue
  fi

  STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_ID" 2>/dev/null)

  if [[ "$STATUS" == "healthy" ]]; then
    echo "✅ $SERVICE está saudável."
  elif [[ "$STATUS" == "unhealthy" ]]; then
    echo "❌ $SERVICE está com problemas (unhealthy)."
    ALL_HEALTHY=false
  else
    echo "⚠️ $SERVICE não possui healthcheck configurado ou está em estado desconhecido."
    ALL_HEALTHY=false
  fi
done

if [ "$ALL_HEALTHY" = true ]; then
  echo "🎉 Todos os serviços do ambiente A estão saudáveis!"
  exit 0
else
  echo "⚠️ Um ou mais serviços estão com problemas. Verifique os logs com 'docker-compose logs'."
  exit 1
fi