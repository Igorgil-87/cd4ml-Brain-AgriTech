#!/usr/bin/env bash
set -Eeuo pipefail

# =========================
# VARIÁVEIS / AJUSTE FÁCIL
# =========================
NS=spinnaker
MYSQL_IMAGE=mariadb:10.6
MYSQL_ROOT_PASSWORD=123
MYSQL_DB=front50
SPIN_VERSION=1.30.1
HAL_IMAGE=us-docker.pkg.dev/spinnaker-community/docker/halyard:stable
HAL_NAME=halyard

# Port-forwards (UI/API)
DECK_LOCAL_PORT=9000
GATE_LOCAL_PORT=8084

echo ">> Passo 0: checagens rápidas"
kubectl version --client >/dev/null
docker version >/dev/null

# =========================================
# 1) Namespace e MySQL (Front50 usa MySQL)
# =========================================
echo ">> Passo 1: Namespace e banco MySQL"
kubectl get ns "$NS" >/dev/null 2>&1 || kubectl create ns "$NS"

kubectl -n "$NS" get pod mysql >/dev/null 2>&1 || \
kubectl -n "$NS" run mysql \
  --image="$MYSQL_IMAGE" \
  --env="MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD" \
  --env="MYSQL_DATABASE=$MYSQL_DB" \
  --port=3306 \
  --restart=Always

kubectl -n "$NS" get svc mysql >/dev/null 2>&1 || \
kubectl -n "$NS" expose pod mysql --name=mysql --port=3306 --target-port=3306

echo "   - Aguardando MySQL ficar Ready..."
kubectl -n "$NS" wait --for=condition=Ready pod/mysql --timeout=180s

# Teste do MySQL
echo ">> Testando MySQL dentro do cluster"
kubectl -n "$NS" run sql-client --rm -it --restart=Never --image="$MYSQL_IMAGE" -- \
  mysql -hmysql -uroot -p"$MYSQL_ROOT_PASSWORD" -e "SHOW DATABASES;" || true

# =========================================
# 2) Sobe o Halyard (em contêiner Docker)
# =========================================
echo ">> Passo 2: Halyard container"
# Monta seu ~/.kube para o Halyard usar o mesmo kubeconfig
docker ps --format '{{.Names}}' | grep -qx "$HAL_NAME" || \
docker run --name "$HAL_NAME" -d \
  -v "$HOME/.kube:/home/spinnaker/.kube" \
  "$HAL_IMAGE" sleep infinity

# Dentro do contêiner, garanta que o kubeconfig aponte para um endpoint acessível do CONTAINER.
# Em Docker Desktop (Mac), use kubernetes.docker.internal:6443; e ignore verificação TLS para evitar erro de SAN.
echo ">> Ajustando kubeconfig dentro do Halyard para falar com o cluster (in-cluster access)"
docker exec -it "$HAL_NAME" bash -lc '
set -Eeuo pipefail
kubectl config current-context >/dev/null
kubectl config set-cluster docker-desktop --server="https://kubernetes.docker.internal:6443" --insecure-skip-tls-verify=true >/dev/null
kubectl get nodes >/dev/null
echo "[halyard] kubectl OK dentro do contêiner"
'

# =========================================
# 3) Configuração do Spinnaker via hal
# =========================================
echo ">> Passo 3: Configurando Spinnaker ($SPIN_VERSION) via hal"
docker exec -it "$HAL_NAME" hal config version edit --version "$SPIN_VERSION"

docker exec -it "$HAL_NAME" hal config provider kubernetes enable
docker exec -it "$HAL_NAME" hal config provider kubernetes account add another-account --context docker-desktop

docker exec -it "$HAL_NAME" hal config deploy edit \
  --type distributed \
  --account-name another-account

# Persistent storage "global" do Spinnaker (não é o Front50)
docker exec -it "$HAL_NAME" hal config storage edit --type redis

# Opcional: features.artifacts (é default nessa versão, não faz mal)
docker exec -it "$HAL_NAME" hal config features edit --artifacts true || true

# Opcional: colocar todos recursos no namespace $NS
docker exec -it "$HAL_NAME" hal config deploy edit --location "$NS"

echo ">> Passo 3.1: Primeiro deploy (vai gerar os manifests)"
docker exec -it "$HAL_NAME" hal -q deploy apply || true

# ==========================================================
# 4) Corrigir Front50 para usar MySQL e NÃO quebrar no YAML
#    (remover o 'spring.profiles.include' do front50-local)
# ==========================================================
echo ">> Passo 4: Criando ConfigMap limpo para front50-local.yml (sem 'spring.profiles.include')"
kubectl -n "$NS" apply -f - <<'YAML'
apiVersion: v1
kind: ConfigMap
metadata:
  name: front50-local
data:
  front50-local.yml: |
    sql:
      enabled: true
      connectionPools:
        default:
          default: true
          jdbcUrl: jdbc:mysql://mysql:3306/front50?useSSL=false
          user: root
          password: 123
          driverClassName: org.mariadb.jdbc.Driver
      migration:
        jdbcUrl: jdbc:mysql://mysql:3306/front50?useSSL=false
        user: root
        password: 123
    spinnaker:
      redis:
        enabled: false
YAML

echo ">> Passo 4.1: Patch no Deployment do front50 para sobrepor o arquivo do Secret do Halyard"
# 4.1.1) Garante um volume emptyDir para /opt/spinnaker/config
kubectl -n "$NS" patch deploy spin-front50 --type='json' -p='[
  {"op":"add","path":"/spec/template/spec/volumes/-","value":{"name":"config-merged","emptyDir":{}}}
]' || true

# 4.1.2) Monta o emptyDir em /opt/spinnaker/config
kubectl -n "$NS" patch deploy spin-front50 --type='json' -p='[
  {"op":"add","path":"/spec/template/spec/containers/0/volumeMounts/-",
   "value":{"name":"config-merged","mountPath":"/opt/spinnaker/config"}}
]' || true

# 4.1.3) Descobre o Secret gerado pelo Halyard (tem front50.yml e spinnaker.yml)
HAL_SECRET="$(kubectl -n "$NS" get deploy spin-front50 -o jsonpath='{.spec.template.spec.volumes[?(@.secret)].secret.secretName}')"
if [[ -n "${HAL_SECRET:-}" ]]; then
  # Monta front50.yml e spinnaker.yml do Secret no diretório novo
  kubectl -n "$NS" patch deploy spin-front50 --type='json' -p="[
    {\"op\":\"add\",\"path\":\"/spec/template/spec/containers/0/volumeMounts/-\",
     \"value\":{\"name\":\"$HAL_SECRET\",\"mountPath\":\"/opt/spinnaker/config/front50.yml\",\"subPath\":\"front50.yml\"}}
  ]" || true
  kubectl -n "$NS" patch deploy spin-front50 --type='json' -p="[
    {\"op\":\"add\",\"path\":\"/spec/template/spec/containers/0/volumeMounts/-\",
     \"value\":{\"name\":\"$HAL_SECRET\",\"mountPath\":\"/opt/spinnaker/config/spinnaker.yml\",\"subPath\":\"spinnaker.yml\"}}
  ]" || true
fi

# 4.1.4) Garante o volume do ConfigMap e monta o front50-local.yml LIMPO
# (cria volume front50-local-cm se ainda não existir)
if ! kubectl -n "$NS" get deploy spin-front50 -o json | jq -e '.spec.template.spec.volumes[]?.name=="front50-local-cm"' >/dev/null; then
  kubectl -n "$NS" patch deploy spin-front50 --type='json' -p='[
    {"op":"add","path":"/spec/template/spec/volumes/-",
     "value":{"name":"front50-local-cm","configMap":{"name":"front50-local"}}}
  ]'
fi

# Remove mounts duplicados para /opt/spinnaker/config/front50-local.yml (se houver)
DUP_INDEXES=$(kubectl -n "$NS" get deploy spin-front50 -o json \
  | jq -r '
    .spec.template.spec.containers[0].volumeMounts
    | to_entries[]
    | select(.value.mountPath=="/opt/spinnaker/config/front50-local.yml")
    | .key' || true)

if [[ -n "${DUP_INDEXES:-}" ]]; then
  # remove do maior índice para o menor
  for IDX in $(echo "$DUP_INDEXES" | sort -rn); do
    kubectl -n "$NS" patch deploy spin-front50 --type='json' -p="[
      {\"op\":\"remove\",\"path\":\"/spec/template/spec/containers/0/volumeMounts/$IDX\"}
    ]" || true
  done
fi

# Monta (agora único) front50-local.yml do ConfigMap
kubectl -n "$NS" patch deploy spin-front50 --type='json' -p='[
  {"op":"add","path":"/spec/template/spec/containers/0/volumeMounts/-",
   "value":{"name":"front50-local-cm","mountPath":"/opt/spinnaker/config/front50-local.yml","subPath":"front50-local.yml"}}
]' || true

# 4.1.5) Variáveis de ambiente finais do front50
kubectl -n "$NS" set env deploy/spin-front50 --overwrite \
  SPRING_PROFILES_ACTIVE='local,sql' \
  SPRING_CONFIG_LOCATION='file:/opt/spinnaker/config/' \
  JAVA_OPTS='-XX:MaxRAMPercentage=50.0 -Dlogging.file.name=/dev/stdout' >/dev/null

echo ">> Reiniciando front50 para aplicar patches"
kubectl -n "$NS" rollout restart deploy/spin-front50
echo "   - Esperando front50 subir..."
kubectl -n "$NS" rollout status deploy/spin-front50 --timeout=300s

# ==========================================================
# 5) Verificações rápidas (health e MySQL reachability)
# ==========================================================
echo ">> Health do front50 via Service interno"
kubectl -n "$NS" run netcheck --rm -it --restart=Never --image=busybox:1.36 -- \
  sh -lc 'wget -qO- http://spin-front50:8080/health || true' || true

# ==========================================================
# 6) Port-forwards da UI (Deck) e API (Gate)
# ==========================================================
echo ">> Passo 6: Port-forward da API (Gate) e UI (Deck)"
# Encerra qualquer port-forward anterior nessas portas
lsof -ti tcp:$GATE_LOCAL_PORT | xargs -r kill -9 || true
lsof -ti tcp:$DECK_LOCAL_PORT | xargs -r kill -9 || true

# Faz port-forward em background e registra PIDs para matar ao sair
kubectl -n "$NS" port-forward svc/spin-gate $GATE_LOCAL_PORT:8084 >/tmp/spin-gate.pf.log 2>&1 &
PF_GATE_PID=$!
kubectl -n "$NS" port-forward svc/spin-deck $DECK_LOCAL_PORT:9000 >/tmp/spin-deck.pf.log 2>&1 &
PF_DECK_PID=$!

cleanup() {
  echo ">> Encerrando port-forwards..."
  kill -9 "${PF_GATE_PID:-0}" "${PF_DECK_PID:-0}" 2>/dev/null || true
}
trap cleanup EXIT

sleep 2
echo
echo "======================================================"
echo " Spinnaker no ar!"
echo " UI (Deck):   http://localhost:${DECK_LOCAL_PORT}"
echo " API (Gate):  http://localhost:${GATE_LOCAL_PORT}"
echo " Dicas:"
echo "  - Logs port-forward: /tmp/spin-gate.pf.log e /tmp/spin-deck.pf.log"
echo "  - Para parar, CTRL+C (este script mata os port-forwards)."
echo "======================================================"
echo

# Mantém o script aberto para sustentar os port-forwards até CTRL+C
# Comente a linha abaixo se preferir encerrar já.
wait