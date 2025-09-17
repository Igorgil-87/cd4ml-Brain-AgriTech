#!/bin/bash
set -e

echo "⚠️  Este script irá APAGAR COMPLETAMENTE os ambientes A, B e o Spinnaker."
read -p "Tem certeza? (digite 'SIM' para continuar): " CONFIRMA

if [[ "$CONFIRMA" != "SIM" ]]; then
  echo "❌ Operação cancelada."
  exit 1
fi

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_A_DIR="$BASE_DIR/dr-infra/env-a"
ENV_B_DIR="$BASE_DIR/dr-infra/env-b"
SPINNAKER_DIR="$BASE_DIR/dr-infra/spinnaker"

echo "⛔ Parando e removendo todos os containers..."
docker compose -f "$ENV_A_DIR/docker-compose.yaml" down -v --remove-orphans || true
docker compose -f "$ENV_B_DIR/docker-compose.yaml" down -v --remove-orphans || true
docker compose -f "$SPINNAKER_DIR/docker-compose.yaml" down -v --remove-orphans || true

echo "🧹 Removendo volumes órfãos..."
docker volume prune -f || true

echo "🔌 Removendo redes órfãs..."
docker network prune -f || true

read -p "Deseja também remover todas as imagens Docker criadas? (digite 'SIM' para confirmar): " IMAGENS_OK
if [[ "$IMAGENS_OK" == "SIM" ]]; then
  echo "🗑️  Removendo imagens criadas localmente (dagster, mlflow, etc)..."
  docker images --filter=reference="*dagster*" --format "{{.Repository}}:{{.Tag}}" | xargs -r docker rmi -f || true
  docker images --filter=reference="*mlflow*" --format "{{.Repository}}:{{.Tag}}" | xargs -r docker rmi -f || true
  docker images --filter=reference="*cd4ml*" --format "{{.Repository}}:{{.Tag}}" | xargs -r docker rmi -f || true
fi

echo "✅ Todos os ambientes foram destruídos com sucesso."