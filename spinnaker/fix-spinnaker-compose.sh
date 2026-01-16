#!/usr/bin/env bash
# fix-spinnaker-compose.sh
# Ajusta RBAC, reinicia Clouddriver/Front50 e aplica um Job de teste (DinD+Compose)
# com diagnóstico de proxy (DNS do proxy dentro do cluster) e logs de sucesso/erro.

set -euo pipefail

# ===================== Defaults =====================
NS="${JOB_NAMESPACE:-spinnaker}"
ACCOUNT="${K8S_ACCOUNT:-another-account}"

CM_YAML="${CM_YAML:-compose-yaml-a}"
CM_ENV="${CM_ENV:-compose-env-a}"
JOB_NAME="${JOB_NAME:-compose-env-a-up}"

HTTP_PROXY="${HTTP_PROXY:-${http_proxy:-}}"
HTTPS_PROXY="${HTTPS_PROXY:-${https_proxy:-}}"
NO_PROXY="${NO_PROXY:-${no_proxy:-}}"

# se só tiver o hostname do proxy mas não resolve no cluster, informe o IP aqui
PROXY_HOST_IP="${PROXY_HOST_IP:-}"

INSECURE_REGISTRY="${INSECURE_REGISTRY:-}"

DIND_REQ_CPU="${DIND_REQ_CPU:-500m}"
DIND_REQ_MEM="${DIND_REQ_MEM:-512Mi}"
CLI_REQ_CPU="${CLI_REQ_CPU:-200m}"
CLI_REQ_MEM="${CLI_REQ_MEM:-256Mi}"

WAIT_TIMEOUT_SEC="${WAIT_TIMEOUT_SEC:-420}"

# ===================== Helpers =====================
say(){ echo -e ">> $*"; }
err(){ echo -e "!! $*" 1>&2; }
need(){ command -v "$1" >/dev/null 2>&1 || { err "Faltando '$1' no PATH"; exit 1; }; }

# normaliza e de-duplica NO_PROXY
uniq_no_proxy() {
  tr ',' '\n' | sed '/^$/d' | awk '!seen[$0]++' | paste -sd, -
}

# extrai host de URL http(s)://user:pass@host:port
extract_host() {
  local u="$1"
  case "$u" in
    http://*|https://*) u="${u#http://}"; u="${u#https://}";;
  esac
  u="${u%%/*}"; u="${u##*@}"
  echo "${u%%:*}"
}

get_api_host() {
  kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}' 2>/dev/null \
    | sed -E 's#^https?://##; s/:.*$//'
}

apply_yaml() { kubectl -n "$NS" apply -f - >/dev/null && echo "OK" || return 1; }

rewrite_proxy_to_ip() {
  # reescreve HTTP(S)_PROXY para usar PROXY_HOST_IP mantendo porta e credenciais
  local url="$1" ip="$2"
  [[ -z "$url" || -z "$ip" ]] && { echo "$url"; return; }
  local scheme cred hostport port
  scheme="${url%%://*}"; scheme="${scheme:-http}"
  local rest="${url#*://}"
  cred=""; hostport="$rest"
  [[ "$rest" == *"@"* ]] && { cred="${rest%%@*}"; hostport="${rest#*@}"; }
  port="${hostport#*:}"; port="${port%%/*}"
  [[ "$port" =~ ^[0-9]+$ ]] || port="3128"
  local new="${scheme}://"
  [[ -n "$cred" ]] && new+="${cred}@"
  new+="${ip}:${port}"
  echo "$new"
}

# ===================== Checks =====================
need kubectl
need jq

CTX="$(kubectl config current-context || true)"
API_HOST="$(get_api_host || true)"
say "Contexto do kubectl: ${CTX:-<desconhecido>}"
say "API server host: ${API_HOST:-<desconhecido>}"

BASE_NO_PROXY="localhost,127.0.0.1,::1,*.local,*.svc,svc,cluster.local,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,kubernetes.default.svc"
[[ -n "${API_HOST:-}" ]] && BASE_NO_PROXY="$BASE_NO_PROXY,$API_HOST"

# agrega e deduplica
echo "$NO_PROXY,$BASE_NO_PROXY" | uniq_no_proxy >/tmp/.np
NO_PROXY="$(cat /tmp/.np)"
say "NO_PROXY efetivo que será injetado no Pod: $NO_PROXY"
echo "HTTP_PROXY=${HTTP_PROXY:-<unset>}"
echo "HTTPS_PROXY=${HTTPS_PROXY:-<unset>}"

# ===================== Proxy DNS pré-checagem =====================
PROXY_URL="${HTTPS_PROXY:-${HTTP_PROXY:-}}"
PROXY_HOST=""
[[ -n "$PROXY_URL" ]] && PROXY_HOST="$(extract_host "$PROXY_URL")"

say "Pré-checagem de proxy dentro do cluster..."
USE_HOST_ALIAS=0
if [[ -n "$PROXY_HOST" ]]; then
  say "  Testando resolução DNS do proxy '$PROXY_HOST' no namespace '$NS'..."
  set +e
  kubectl -n "$NS" run proxy-dns-check-$$ --image=busybox:1.36 --restart=Never --rm -it --command -- \
      sh -lc "nslookup $PROXY_HOST >/dev/null 2>&1 || getent hosts $PROXY_HOST >/dev/null 2>&1"
  rc=$?
  set -e
  if [[ $rc -ne 0 ]]; then
    err "  FALHA: '$PROXY_HOST' não resolve via DNS do cluster."
    if [[ -n "$PROXY_HOST_IP" ]]; then
      say "  Vou usar PROXY_HOST_IP=$PROXY_HOST_IP (hostAliases) e reescrever HTTP(S)_PROXY para IP."
      USE_HOST_ALIAS=1
      [[ -n "$HTTP_PROXY"  ]] && HTTP_PROXY="$(rewrite_proxy_to_ip "$HTTP_PROXY"  "$PROXY_HOST_IP")"
      [[ -n "$HTTPS_PROXY" ]] && HTTPS_PROXY="$(rewrite_proxy_to_ip "$HTTPS_PROXY" "$PROXY_HOST_IP")"
    else
      err "     • Informe PROXY_HOST_IP (ex.: export PROXY_HOST_IP=10.20.30.40) ou use diretamente o IP nas variáveis HTTP(S)_PROXY."
      exit 1
    fi
  else
    echo "  OK: '$PROXY_HOST' resolve no cluster."
  fi
else
  say "  Nenhuma variável HTTPS_PROXY/HTTP_PROXY definida. Se a rede exigir proxy, os pulls podem falhar."
fi

# ===================== Namespace e SA =====================
if ! kubectl get ns "$NS" >/dev/null 2>&1; then
  err "Namespace '$NS' não existe"; exit 1
fi

discover_sa() {
  local sa="spin-clouddriver"
  if kubectl -n "$NS" get deploy spin-clouddriver >/dev/null 2>&1; then
    sa="$(kubectl -n "$NS" get deploy spin-clouddriver -o jsonpath='{.spec.template.spec.serviceAccountName}')"
    [[ -z "$sa" ]] && sa="spin-clouddriver"
  fi
  echo "$sa"
}
SA_CLOUDDRIVER="$(discover_sa)"
say "ServiceAccount do Clouddriver: ${SA_CLOUDDRIVER} (ns=${NS})"

# ===================== RBAC mínimo =====================
say "Aplicando Role/RoleBinding para Jobs/Pods/ConfigMaps/Logs..."
cat <<YAML | apply_yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: spinnaker-manifests
  namespace: ${NS}
rules:
  - apiGroups: ["batch"]
    resources: ["jobs"]
    verbs: ["get","list","watch","create","update","patch","delete"]
  - apiGroups: [""]
    resources: ["pods","pods/log","configmaps","events"]
    verbs: ["get","list","watch","create","update","patch","delete"]
  - apiGroups: ["apps"]
    resources: ["deployments","replicasets"]
    verbs: ["get","list","watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: spinnaker-manifests-binding
  namespace: ${NS}
subjects:
  - kind: ServiceAccount
    name: ${SA_CLOUDDRIVER}
    namespace: ${NS}
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: spinnaker-manifests
YAML

say "Validando permissões (can-i) ..."
kubectl -n "$NS" auth can-i create jobs --as="system:serviceaccount:${NS}:${SA_CLOUDDRIVER}" || true
kubectl -n "$NS" auth can-i get configmaps/"${CM_YAML}" --as="system:serviceaccount:${NS}:${SA_CLOUDDRIVER}" || true
kubectl -n "$NS" auth can-i get configmaps/"${CM_ENV}"  --as="system:serviceaccount:${NS}:${SA_CLOUDDRIVER}" || true

# ===================== Rollouts =====================
restart_and_wait() {
  local d="$1"
  say "Rollout restart ${d} ..."
  kubectl -n "$NS" rollout restart "deploy/${d}" >/dev/null || true
  say "Aguardando readiness ${d} ..."
  if ! kubectl -n "$NS" rollout status "deploy/${d}" --timeout=180s; then
    err "Deploy ${d} não ficou pronto"
    kubectl -n "$NS" get pods -l "cluster=${d}" -o wide || true
  fi
}
restart_and_wait "spin-clouddriver"
restart_and_wait "spin-front50"

# ===================== ConfigMaps =====================
say "Checando ConfigMaps (compose YAML/ENV) ..."
kubectl -n "$NS" get cm "${CM_YAML}" >/dev/null 2>&1 || { err "ConfigMap ${CM_YAML} não encontrado"; exit 1; }
kubectl -n "$NS" get cm "${CM_ENV}"  >/dev/null 2>&1 || kubectl -n "$NS" create configmap "${CM_ENV}" --from-literal=".env=" >/dev/null

# ===================== Job (DinD + socket UNIX; PROXY/NO_PROXY nos 2 contêineres) =====================
say "Apagando Job antigo (se existir) ${JOB_NAME} ..."
kubectl -n "$NS" delete job "${JOB_NAME}" --ignore-not-found >/dev/null || true

say "Aplicando Job ${JOB_NAME} (socket UNIX + PROXY/NO_PROXY) ..."
DIND_ARGS='["--host=tcp://0.0.0.0:2375","--tls=false","--storage-driver=overlay2"'
[[ -n "${INSECURE_REGISTRY}" ]] && DIND_ARGS="${DIND_ARGS},\"--insecure-registry=${INSECURE_REGISTRY}\""
DIND_ARGS="${DIND_ARGS}]"

HOSTALIASES_BLOCK=""
if [[ "$USE_HOST_ALIAS" -eq 1 && -n "$PROXY_HOST_IP" && -n "$PROXY_HOST" ]]; then
  HOSTALIASES_BLOCK=$(cat <<EOF
      hostAliases:
        - ip: "${PROXY_HOST_IP}"
          hostnames: ["${PROXY_HOST}"]
EOF
)
fi

cat <<YAML | apply_yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: ${JOB_NAME}
  annotations:
    strategy.spinnaker.io/replace: "true"
spec:
  backoffLimit: 0
  template:
    spec:
${HOSTALIASES_BLOCK}
      restartPolicy: Never
      securityContext:
        runAsUser: 0
      volumes:
        - name: v-compose
          configMap: { name: ${CM_YAML} }
        - name: v-env
          configMap: { name: ${CM_ENV} }
        - name: run-sock
          emptyDir: {}
        - name: dind-storage
          emptyDir: { sizeLimit: "20Gi" }
      containers:
        - name: dind
          image: docker:27-dind
          imagePullPolicy: IfNotPresent
          securityContext: { privileged: true }
          args: ${DIND_ARGS}
          env:
            - { name: HTTPS_PROXY, value: "${HTTPS_PROXY}" }
            - { name: HTTP_PROXY,  value: "${HTTP_PROXY}"  }
            - { name: NO_PROXY,    value: "${NO_PROXY}"    }
            - { name: no_proxy,    value: "${NO_PROXY}"    }
          resources:
            requests: { cpu: "${DIND_REQ_CPU}", memory: "${DIND_REQ_MEM}" }
          volumeMounts:
            - { name: run-sock,     mountPath: /var/run }
            - { name: dind-storage, mountPath: /var/lib/docker }
        - name: cli
          image: docker:27-cli
          imagePullPolicy: IfNotPresent
          env:
            - { name: DOCKER_HOST,          value: "unix:///var/run/docker.sock" }
            - { name: COMPOSE_PROJECT_NAME, value: "cd4ml" }
            - { name: COMPOSE_STACK,        value: "${JOB_NAME#compose-}" }
            - { name: HTTPS_PROXY,          value: "${HTTPS_PROXY}" }
            - { name: HTTP_PROXY,           value: "${HTTP_PROXY}"  }
            - { name: NO_PROXY,             value: "${NO_PROXY}"    }
            - { name: no_proxy,             value: "${NO_PROXY}"    }
          command: ["sh","-lc"]
          args:
            - |
              set -euo pipefail
              echo '[docker] Esperando /var/run/docker.sock...'
              for i in \$(seq 1 600); do
                [ -S /var/run/docker.sock ] && break
                echo "aguardando socket... (\$i)"; sleep 1
              done
              docker version

              ENV_FILE_ARG=''
              [ -s /configs/.env ] && ENV_FILE_ARG='--env-file /configs/.env'

              echo '[compose] pull/build'
              docker compose -f /configs/docker-compose.yaml \$ENV_FILE_ARG -p "\${COMPOSE_STACK}" pull  || true
              docker compose -f /configs/docker-compose.yaml \$ENV_FILE_ARG -p "\${COMPOSE_STACK}" build --pull || true

              echo '[compose] up -d ...'
              docker compose -f /configs/docker-compose.yaml \$ENV_FILE_ARG -p "\${COMPOSE_STACK}" up -d || true

              echo '[compose] containers'
              docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' || true

              echo "Compose \${COMPOSE_STACK} concluído"
          resources:
            requests: { cpu: "${CLI_REQ_CPU}", memory: "${CLI_REQ_MEM}" }
          volumeMounts:
            - { name: v-compose,  mountPath: /configs/docker-compose.yaml, subPath: docker-compose.yaml }
            - { name: v-env,      mountPath: /configs/.env,                subPath: .env }
            - { name: run-sock,   mountPath: /var/run }
YAML

# ===================== Espera + Logs + Veredito =====================
say "Aguardando Pod ficar Ready (${WAIT_TIMEOUT_SEC}s) ..."
set +e
kubectl -n "$NS" wait --for=condition=Ready pod -l "job-name=${JOB_NAME}" --timeout="${WAIT_TIMEOUT_SEC}s"
set -e

POD="$(kubectl -n "$NS" get pod -l job-name=${JOB_NAME} -o jsonpath='{.items[?(@.status.phase=="Running")].metadata.name}' 2>/dev/null || true)"
[[ -z "${POD:-}" ]] && POD="$(kubectl -n "$NS" get pod -l job-name=${JOB_NAME} -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || true)"

kubectl -n "$NS" get job,pod -l "job-name=${JOB_NAME}" -o wide || true

if [[ -n "${POD:-}" ]]; then
  say "Logs dind (tail-200):"
  kubectl -n "$NS" logs "$POD" -c dind --tail=200 || true

  say "Logs cli  (tail-400):"
  kubectl -n "$NS" logs "$POD" -c cli --tail=400 || true

  say "Verificando sucesso a partir dos logs do 'cli'..."
  set +e
  CLI_LOG="$(kubectl -n "$NS" logs "$POD" -c cli --tail=-1 2>/dev/null)"
  set -e

  SUCCESS=0
  echo "$CLI_LOG" | grep -q "Compose .* concluído" && SUCCESS=1

  if echo "$CLI_LOG" | grep -qiE 'Get "https://registry-1\.docker\.io/v2/": proxyconnect|Client sent an HTTP request to an HTTPS server|no such host'; then
    err "Detectado erro de proxy/pull nas imagens."
    echo "Dicas:"
    echo " • Prefira usar IP do proxy em HTTP(S)_PROXY OU informe PROXY_HOST_IP para hostAliases."
    echo " • Verifique se o proxy aceita CONNECT para HTTPS (Docker Hub requer HTTPS)."
    echo " • Adicione registries internos ao NO_PROXY e, se forem HTTP, use INSECURE_REGISTRY."
  fi

  if echo "$CLI_LOG" | grep -qi 'lstat /configs/'; then
    err "Detectado erro de 'build' por falta de contexto no compose."
    echo " • Serviços com 'build:' precisam de contexto; use imagem publicada ou traga o contexto via PVC/initContainer."
  fi

  if [[ "$SUCCESS" -eq 1 ]]; then
    say "✅ SUCESSO: encontrado 'Compose ... concluído' nos logs."
    exit 0
  else
    err "⚠ O Job rodou, mas não confirmou sucesso."
    exit 1
  fi
else
  err "Não foi possível identificar o Pod do Job para coletar logs."
  exit 1
fi