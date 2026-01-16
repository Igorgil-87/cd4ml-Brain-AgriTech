#!/bin/bash

echo "======================================"
echo " 🧨 RESET DOCKER + KUBERNETES (kubectl)"
echo " Isso vai apagar TUDO do cluster atual:"
echo " - TODOS os namespaces (exceto kube-system, etc. se travados)"
echo " - TODOS os pods, deployments, services, etc."
echo " E depois limpar Docker (containers, imagens, volumes, redes)."
echo "======================================"
echo

kubectl config current-context 2>/dev/null || {
  echo "kubectl não configurado ou sem contexto. Pulando parte de Kubernetes."
}

read -p "DIGITE EXATAMENTE 'SIM' para continuar: " CONFIRM
if [ "$CONFIRM" != "SIM" ]; then
  echo "Cancelado."
  exit 0
fi

echo "🧨 Apagando todos os namespaces Kubernetes (exceto os protegidos)..."
kubectl delete ns --all --force --grace-period=0 2>/dev/null || true

echo "🧨 Apagando PersistentVolumes (se existirem)..."
kubectl delete pv --all 2>/dev/null || true

echo "⛔ Parando containers Docker..."
docker stop $(docker ps -aq) 2>/dev/null || true

echo "🗑️ Removendo containers..."
docker rm -f $(docker ps -aq) 2>/dev/null || true

echo "🧹 Removendo imagens..."
docker rmi -f $(docker images -aq) 2>/dev/null || true

echo "📦 Removendo volumes..."
docker volume rm $(docker volume ls -q) 2>/dev/null || true

echo "🌐 Removendo redes..."
docker network rm $(docker network ls -q) 2>/dev/null || true

echo "🧽 docker system prune..."
docker system prune -a --volumes -f

echo "🔨 Limpando builders..."
docker builder prune -a -f

echo
echo "======================================"
echo " ✅ DOCKER + KUBERNETES RESETADOS (até onde o sistema permitiu)."
echo "   Se usar Docker Desktop, ainda pode haver containers internos"
echo "   (docker-desktop, infra) se o Kubernetes estiver habilitado."
echo "======================================"