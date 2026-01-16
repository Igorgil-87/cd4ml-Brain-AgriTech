#!/bin/bash
set -euo pipefail

echo "🧹 [INÍCIO] Destruição completa do ambiente Spinnaker"
echo "⏰ Iniciado em: $(date)"
echo ""

# 1. Deletar cluster KIND
echo "🔍 Verificando se o cluster KIND 'spinnaker' existe..."
if kind get clusters | grep -q '^spinnaker$'; then
  echo "🗑️ Deletando cluster KIND 'spinnaker'..."
  kind delete cluster --name spinnaker
  echo "✅ Cluster 'spinnaker' removido com sucesso."
else
  echo "⚠️ Cluster 'spinnaker' não encontrado. Nada a remover."
fi
echo ""

# 2. Remover container Halyard
echo "🔍 Verificando se o container 'halyard' está em execução..."
if docker ps -a --format '{{.Names}}' | grep -q '^halyard$'; then
  echo "🗑️ Removendo container 'halyard'..."
  docker rm -f halyard
  echo "✅ Container 'halyard' removido com sucesso."
else
  echo "⚠️ Container 'halyard' não encontrado. Nada a remover."
fi
echo ""

# 3. Remover pod MySQL (se possível)
echo "🔍 Verificando pod 'mysql' no cluster..."
if kubectl get pod mysql &>/dev/null; then
  echo "🗑️ Deletando pod 'mysql'..."
  kubectl delete pod mysql || true
else
  echo "⚠️ Pod 'mysql' não encontrado (ou cluster já está offline)."
fi

echo "🔍 Verificando service 'mysql' no cluster..."
if kubectl get service mysql &>/dev/null; then
  echo "🗑️ Deletando service 'mysql'..."
  kubectl delete service mysql || true
else
  echo "⚠️ Service 'mysql' não encontrado (ou cluster já está offline)."
fi
echo ""

# 4. Resetar contexto inválido do kubectl
echo "🔧 Verificando contexto atual do kubectl..."
CURRENT_CONTEXT=$(kubectl config current-context 2>/dev/null || echo "none")
if [[ "$CURRENT_CONTEXT" == kind-spinnaker ]]; then
  echo "🧹 Limpando contexto inválido 'kind-spinnaker'..."
  kubectl config unset current-context || true
else
  echo "ℹ️ Contexto atual: $CURRENT_CONTEXT (não é o cluster KIND)"
fi
echo ""

# 5. Limpeza de arquivos temporários
echo "🧼 Limpando pastas temporárias usadas por Halyard..."
rm -rf temp_hal &>/dev/null || true
rm -rf ~/.hal/default/staging &>/dev/null || true
rm -rf ~/.hal/.boms &>/dev/null || true
echo "✅ Diretórios temporários removidos."

echo ""
echo "✅ [FINALIZADO] Ambiente destruído com sucesso."
echo "📌 Pronto para recriar com: ./01-create-cluster.sh"