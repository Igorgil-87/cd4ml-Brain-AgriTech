#!/bin/bash
function check_health() {
  SERVICE_NAME=$1
  echo "🔍 Verificando saúde do serviço: $SERVICE_NAME"
  STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$SERVICE_NAME")
  echo "🔄 Status atual: $STATUS"
  if [ "$STATUS" != "healthy" ]; then
    echo "❌ Serviço $SERVICE_NAME não está saudável"
    exit 1
  fi
  echo "✅ Serviço $SERVICE_NAME está saudável"
}