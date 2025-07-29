#!/bin/bash

set -euo pipefail

echo "📦 [INÍCIO] Setup automatizado do Spinnaker com validações e segurança"

echo "🔍 Verificando se cluster KIND 'spinnaker' já existe..."
if kind get clusters | grep -q '^spinnaker$'; then
  echo "✅ Cluster 'spinnaker' já existe, pulando criação."
else
  echo "🚀 Criando cluster KIND 'spinnaker'..."
  kind create cluster --name spinnaker
fi

echo "🔍 Verificando se pod MySQL já existe..."
if kubectl get pod mysql &>/dev/null; then
  echo "✅ Pod MySQL já está criado."
else
  echo "🐬 Criando pod MySQL no cluster..."
  kubectl run mysql \
    --image=mariadb:10.2 \
    --env="MYSQL_ROOT_PASSWORD=123" \
    --env="MYSQL_DATABASE=front50" \
    --port=3306
  kubectl expose pod mysql --port=3306 --target-port=3306 --name=mysql
fi

echo "⏳ Aguardando MySQL ficar pronto..."
kubectl wait --for=condition=Ready pod/mysql --timeout=120s || {
  echo "❌ MySQL não ficou pronto a tempo. Abortando."; exit 1;
}

echo "🔍 Verificando se container 'halyard' já está rodando..."
if docker ps --format '{{.Names}}' | grep -q '^halyard$'; then
  echo "✅ Container 'halyard' já está em execução."
else
  echo "🐳 Iniciando container Halyard..."
  docker run -d --name halyard \
    -v ~/.kube:/home/spinnaker/.kube \
    -v ~/.hal:/home/spinnaker/.hal \
    -p 8064:8064 \
    --network host \
    us-docker.pkg.dev/spinnaker-community/docker/halyard:stable
  sleep 10
fi

echo "⏳ Aguardando Halyard ficar pronto para comandos..."
START_TIME=$(date +%s)
TIMEOUT=90  # máximo 90 segundos
RETRY_INTERVAL=3

while true; do
  if docker exec halyard hal -v &>/dev/null; then
    echo "✅ Halyard pronto para uso!"
    break
  fi

  CURRENT_TIME=$(date +%s)
  ELAPSED=$((CURRENT_TIME - START_TIME))

  if [ "$ELAPSED" -ge "$TIMEOUT" ]; then
    echo "❌ Tempo limite excedido esperando o Halyard responder. Verifique com: docker logs halyard"
    exit 1
  fi

  echo "⌛ Halyard ainda iniciando... ($ELAPSED s)"
  sleep $RETRY_INTERVAL
done
echo "✅ Halyard pronto para uso!"

echo "⚙️ Executando configurações dentro do Halyard..."
docker exec -i halyard bash <<'EOF'
set -e

echo "🔧 Configurando versão do Spinnaker..."
hal config version edit --version 1.30.1 || true

echo "🔧 Habilitando provider Kubernetes..."
hal config provider kubernetes enable || true

echo "🔍 Verificando se conta 'my-k8s-account' já existe..."
if ! hal config provider kubernetes account list | grep -q 'my-k8s-account'; then
  echo "➕ Adicionando conta 'my-k8s-account'..."
  hal config provider kubernetes account add my-k8s-account --context kind-spinnaker
else
  echo "✅ Conta 'my-k8s-account' já está configurada."
fi

echo "🔧 Configurando ambiente de deploy distribuído..."
hal config deploy edit --type distributed --account-name my-k8s-account || true

echo "💾 Configurando armazenamento usando MySQL (front50)..."
mkdir -p /home/spinnaker/.hal/default/profiles
cat > /home/spinnaker/.hal/default/profiles/front50-local.yml <<EOC
sql:
  enabled: true
  connectionPools:
    default:
      default: true
      jdbcUrl: jdbc:mysql://mysql.default.svc.cluster.local:3306/front50
      user: root
      password: 123
  migration:
    user: root
    password: 123
    jdbcUrl: jdbc:mysql://mysql.default.svc.cluster.local:3306/front50
spinnaker:
  redis:
    enabled: false
EOC

echo "🚀 Aplicando deploy do Spinnaker..."
hal deploy apply || true
EOF

echo "⏳ Aguardando namespace 'spinnaker' existir..."
until kubectl get ns spinnaker &>/dev/null; do
  echo "⌛ Aguardando criação do namespace 'spinnaker'..."
  sleep 5
done

echo "📊 Aguardando pods do Spinnaker estarem prontos..."
kubectl wait --for=condition=Ready pods --all -n spinnaker --timeout=300s || {
  echo "⚠️ Nem todos os pods ficaram prontos a tempo. Verifique com: kubectl get pods -n spinnaker"
}
kubectl get pods -n spinnaker

echo "🌐 Verificando se Ingress já foi criado..."
if kubectl get ingress -n spinnaker spinnaker-ingress &>/dev/null; then
  echo "✅ Ingress já existe."
else
  echo "📥 Criando Ingress para acessar o Spinnaker via spinnaker.local..."
  cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: spinnaker-ingress
  namespace: spinnaker
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: spinnaker.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: spin-deck
            port:
              number: 9000
EOF
fi

echo ""
echo "✅ [FINALIZADO] Spinnaker instalado com sucesso!"
echo "🌍 Acesse via navegador: http://spinnaker.local"
echo "💡 Adicione ao /etc/hosts se necessário: 127.0.0.1 spinnaker.local"
echo "👀 Para acompanhar os pods em tempo real, execute:"
echo "    watch kubectl get pods -n spinnaker"