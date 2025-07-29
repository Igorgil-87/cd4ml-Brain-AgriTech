#!/bin/bash
set -euo pipefail

echo "🧨 [RESET] Destruindo ambiente KIND + Docker Compose + volumes..."

# 1. Parar e remover todos os containers do Docker Compose
echo "🛑 Parando containers do Docker Compose..."
docker-compose down -v --remove-orphans || true

# 2. Remover o cluster KIND 'spinnaker'
if kind get clusters | grep -q '^spinnaker$'; then
  echo "🗑️ Removendo cluster KIND 'spinnaker'..."
  kind delete cluster --name spinnaker
else
  echo "⚠️ Cluster KIND 'spinnaker' não encontrado, pulando remoção."
fi

# 3. Remover volumes Docker específicos do seu projeto
echo "🧹 Removendo volumes específicos do projeto..."
docker volume rm \
  cd4ml-brain-agritech_jenkins_home \
  cd4ml-brain-agritech_data01 \
  cd4ml-brain-agritech_minio-storage \
  cd4ml-brain-agritech_mlflow-storage \
  cd4ml-brain-agritech_postgres_data || true

# 4. Remover diretórios de configuração do Spinnaker (halyard)
echo "🧨 Removendo diretórios .hal e .kube do Spinnaker (use com cuidado!)"
rm -rf ~/.hal ~/.kube || true

# 5. Parar e remover container do Halyard se ainda estiver rodando
if docker ps -a --format '{{.Names}}' | grep -q '^halyard$'; then
  echo "🗑️ Removendo container Halyard..."
  docker rm -f halyard || true
fi

echo "✅ Ambiente completamente destruído."

echo ""
echo "🚀 Iniciando reconstrução automática..."
./setup_spinnaker.sh