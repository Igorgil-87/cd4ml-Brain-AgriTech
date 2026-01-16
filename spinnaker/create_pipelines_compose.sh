#!/usr/bin/env bash
# Compatível com Bash 3.2 (macOS)

set -euo pipefail

# ===================== ENV REQUERIDAS (ajuste se precisar) =====================
export K8S_ACCOUNT="${K8S_ACCOUNT:-another-account}"
export JOB_NAMESPACE="${JOB_NAMESPACE:-spinnaker}"

export PATH_COMPOSE_A="${PATH_COMPOSE_A:-$PWD/dr-infra/env-a/docker-compose.yaml}"
export ENV_FILE_A="${ENV_FILE_A:-$PWD/dr-infra/env-a/.env}"

export PATH_COMPOSE_B="${PATH_COMPOSE_B:-$PWD/dr-infra/env-b/docker-compose.yaml}"
export ENV_FILE_B="${ENV_FILE_B:-$PWD/dr-infra/env-b/.env}"

# ===================== Config do Gate/Spinnaker =====================
GATE_URL="${GATE_URL:-http://localhost:8084}"
APP_NAME="${APP_NAME:-demo-app}"
PIPELINE_USER="${PIPELINE_USER:-vanessa}"
SKIP_EXPRESSION_EVAL="true"

# ===================== Helpers =====================
say()  { echo ">> $*"; }
err()  { echo "!! $*" 1>&2; }
need() { command -v "$1" >/dev/null 2>&1 || { err "Faltando '$1'"; exit 1; }; }

pretty_env() {
  case "$1" in
    env-a) echo "Env-a" ;;
    env-b) echo "Env-b" ;;
    *)     echo "$1" ;;
  esac
}

check_bin() {
  need curl
  need jq
  need kubectl
}

check_envs() {
  [ -n "${K8S_ACCOUNT:-}" ]    || { err "Defina K8S_ACCOUNT"; exit 1; }
  [ -n "${JOB_NAMESPACE:-}" ]  || { err "Defina JOB_NAMESPACE"; exit 1; }
  [ -n "${PATH_COMPOSE_A:-}" ] || { err "Defina PATH_COMPOSE_A"; exit 1; }
  [ -n "${PATH_COMPOSE_B:-}" ] || { err "Defina PATH_COMPOSE_B"; exit 1; }
  [ -f "${PATH_COMPOSE_A}" ]   || { err "Arquivo não encontrado: $PATH_COMPOSE_A"; exit 1; }
  [ -f "${PATH_COMPOSE_B}" ]   || { err "Arquivo não encontrado: $PATH_COMPOSE_B"; exit 1; }
  # ENV_FILE_A / ENV_FILE_B são opcionais
}

check_gate() {
  say "Verificando Gate em ${GATE_URL}/health ..."
  curl -fsS "${GATE_URL}/health" >/dev/null || { err "Gate indisponível em ${GATE_URL}"; exit 1; }
  echo "OK"
}

ensure_app() {
  say "Garantindo aplicação '${APP_NAME}' ..."
  if curl -fsS "${GATE_URL}/applications/${APP_NAME}/pipelineConfigs" >/dev/null 2>&1; then
    echo "Aplicação já existe."
    return 0
  fi
  curl -fsS -X POST -H "Content-Type: application/json" \
    -H "X-Spinnaker-User: ${PIPELINE_USER}" \
    -d "{\"name\":\"${APP_NAME}\",\"email\":\"devnull@example.com\"}" \
    "${GATE_URL}/applications" >/dev/null || true
}

apply_cm_file() {
  # $1 cm_name ; $2 key ; $3 path
  local cm="$1" key="$2" file="$3"
  if [ -f "$file" ]; then
    kubectl create configmap "$cm" \
      --from-file="${key}=${file}" \
      -n "${JOB_NAMESPACE}" \
      --dry-run=client -o yaml | kubectl apply -f - >/dev/null
    echo "configmap/${cm} configured"
  else
    err "Arquivo não encontrado: $file (pulando CM ${cm})"
  fi
}

apply_compose_configmaps() {
  say "Aplicando ConfigMaps dos compose (A)..."
  apply_cm_file "compose-yaml-a" "docker-compose.yaml" "${PATH_COMPOSE_A}"
  if [ -n "${ENV_FILE_A:-}" ] && [ -f "${ENV_FILE_A}" ]; then
    apply_cm_file "compose-env-a" ".env" "${ENV_FILE_A}"
  else
    kubectl -n "${JOB_NAMESPACE}" create configmap "compose-env-a" \
      --from-literal=".env=" --dry-run=client -o yaml | kubectl apply -f - >/dev/null
    echo "configmap/compose-env-a (vazio) configured"
  fi
  echo "ConfigMap compose-env-a aplicado."

  say "Aplicando ConfigMaps dos compose (B)..."
  apply_cm_file "compose-yaml-b" "docker-compose.yaml" "${PATH_COMPOSE_B}"
  if [ -n "${ENV_FILE_B:-}" ] && [ -f "${ENV_FILE_B}" ]; then
    apply_cm_file "compose-env-b" ".env" "${ENV_FILE_B}"
  else
    kubectl -n "${JOB_NAMESPACE}" create configmap "compose-env-b" \
      --from-literal=".env=" --dry-run=client -o yaml | kubectl apply -f - >/dev/null
    echo "configmap/compose-env-b (vazio) configured"
  fi
  echo "ConfigMap compose-env-b aplicado."
}

# Comando que roda dentro do contêiner "cli"
make_cli_cmd() {
  # Heredoc literal (NÃO expande aqui; expande dentro do pod)
  cat <<'EOS'
set -euo pipefail

apk add --no-cache bash curl jq coreutils >/dev/null

echo '[docker] Aguardando dockerd do sidecar...'
for i in $(seq 1 120); do
  if DOCKER_HOST=tcp://localhost:2375 docker version >/dev/null 2>&1; then break; fi
  echo "Aguardando dockerd... ($i)"; sleep 2
done

ENV_FILE_ARG=''
if [ -s /configs/.env ]; then
  ENV_FILE_ARG='--env-file /configs/.env'
fi

echo '[compose] Pull/Build (cache/rede)'
DOCKER_HOST=tcp://localhost:2375 docker compose -f /configs/docker-compose.yaml $ENV_FILE_ARG -p "${COMPOSE_STACK}" pull  || true
DOCKER_HOST=tcp://localhost:2375 docker compose -f /configs/docker-compose.yaml $ENV_FILE_ARG -p "${COMPOSE_STACK}" build --pull || true

echo '[compose] up -d ...'
DOCKER_HOST=tcp://localhost:2375 docker compose -f /configs/docker-compose.yaml $ENV_FILE_ARG -p "${COMPOSE_STACK}" up -d

echo '[compose] containers:'
DOCKER_HOST=tcp://localhost:2375 docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

echo "Compose ${COMPOSE_STACK} concluído"
EOS
}

build_job_json() {
  # $1 env_code ("env-a" | "env-b")
  local env_code="$1"
  local cm_yaml cm_env job_name app_label
  if [ "$env_code" = "env-a" ]; then
    cm_yaml="compose-yaml-a"; cm_env="compose-env-a"
  else
    cm_yaml="compose-yaml-b"; cm_env="compose-env-b"
  fi
  job_name="compose-${env_code}-up"
  app_label="$job_name"

  local CMD; CMD="$(make_cli_cmd)"

  jq -n \
    --arg job "$job_name" \
    --arg app "$app_label" \
    --arg cm_yaml "$cm_yaml" \
    --arg cm_env  "$cm_env" \
    --arg cmd "$CMD" \
    '{
      apiVersion: "batch/v1",
      kind: "Job",
      metadata: {
        name: $job,
        annotations: { "strategy.spinnaker.io/replace": "true" }
      },
      spec: {
        backoffLimit: 0,
        template: {
          metadata: { labels: { app: $app } },
          spec: {
            dnsPolicy: "ClusterFirst",
            hostNetwork: false,
            restartPolicy: "Never",
            securityContext: { runAsUser: 0 },
            volumes: [
              { name:"v-compose",    configMap:{ name: $cm_yaml } },
              { name:"v-env",        configMap:{ name: $cm_env  } },
              { name:"dind-storage", emptyDir:{ sizeLimit:"20Gi" } }
            ],
            containers: [
              {
                name: "cli",
                image: "docker:27-cli",
                imagePullPolicy: "IfNotPresent",
                env: [
                  { name:"DOCKER_HOST",           value:"tcp://localhost:2375" },
                  { name:"COMPOSE_PROJECT_NAME",  value:"cd4ml" },
                  { name:"COMPOSE_STACK",         value: ($job | sub("^compose-";"") | sub("-up$";"")) }
                ],
                resources: {
                  requests: { cpu:"500m", memory:"512Mi" },
                  limits:   { cpu:"2",    memory:"4Gi"   }
                },
                command: ["sh","-lc", $cmd],
                volumeMounts: [
                  { name:"v-compose", mountPath:"/configs/docker-compose.yaml", subPath:"docker-compose.yaml" },
                  { name:"v-env",     mountPath:"/configs/.env",                subPath:".env" }
                ]
              },
              {
                name: "dind",
                image: "docker:27-dind",
                imagePullPolicy: "IfNotPresent",
                args: ["--host=tcp://0.0.0.0:2375","--tls=false","--storage-driver=overlay2","--mtu=1450"],
                securityContext: { privileged: true },
                resources: {
                  requests: { cpu:"1000m", memory:"1Gi" },
                  limits:   { cpu:"3",     memory:"6Gi" }
                },
                volumeMounts: [ { name:"dind-storage", mountPath:"/var/lib/docker" } ]
              }
            ]
          }
        }
      }
    }'
}

build_delete_stage_json() {
  # $1 env_code
  local env_code="$1"
  local job="compose-${env_code}-up"
  jq -n \
    --arg name "Delete antigo (${env_code})" \
    --arg account "$K8S_ACCOUNT" \
    --arg ns "$JOB_NAMESPACE" \
    --arg manifest "job ${job}" \
    '{
      type:"deleteManifest",
      name:$name,
      refId:"0",
      requisiteStageRefIds:[],
      cloudProvider:"kubernetes",
      account:$account,
      mode:"static",
      location:$ns,
      manifestName:$manifest,
      options:{ cascading:true, gracePeriodSeconds:0 }
    }'
}

build_deploy_stage_json() {
  # $1 env_code ; $2 job_json
  local env_code="$1" job_json="$2"
  local stage_name="Compose $(pretty_env "$env_code") Up (deploy)"
  jq -n \
    --arg name "$stage_name" \
    --arg account "$K8S_ACCOUNT" \
    --arg ns "$JOB_NAMESPACE" \
    --arg app "$APP_NAME" \
    --argjson manifests "[$job_json]" \
    --arg skip "${SKIP_EXPRESSION_EVAL}" \
    '{
      type:"deployManifest",
      name:$name,
      refId:"1",
      requisiteStageRefIds:["0"],
      cloudProvider:"kubernetes",
      account:$account,
      source:"text",
      manifests: $manifests,
      moniker:{app:$app},
      namespaceOverride:$ns,
      skipExpressionEvaluation: ($skip=="true"),
      trafficManagement:{enabled:false, options:{enableTraffic:false, services:[]}}
    }'
}

build_webhook_stage_json() {
  # $1 env_code
  local env_code="$1"
  local job="compose-${env_code}-up"
  local url="${GATE_URL}/manifests/${K8S_ACCOUNT}/${JOB_NAMESPACE}/job%20${job}"
  jq -n \
    --arg name "Aguardar Job ${env_code} (Succeeded)" \
    --arg url "$url" \
    --arg user "$PIPELINE_USER" \
    '{
      type:"webhook",
      name:$name,
      refId:"2",
      requisiteStageRefIds:["1"],
      method:"GET",
      url:$url,
      customHeaders:{ "X-Spinnaker-User":[ $user ] },
      waitForCompletion:true,
      successStatuses:["200"],
      statusJsonPath:"$.manifest.status.succeeded",
      successPayloadConstraints:{ "manifest.status.succeeded":"1" },
      progressJsonPath:"$.manifest.metadata.name",
      waitBeforeMonitor:5
    }'
}

pipeline_exists() {
  local pname="$1"
  curl -fsS -H "X-Spinnaker-User: ${PIPELINE_USER}" \
    "${GATE_URL}/applications/${APP_NAME}/pipelineConfigs" \
    | jq -e --arg n "$pname" '.[] | select(.name == $n)' >/dev/null
}

get_pipeline_id() {
  local pname="$1"
  curl -fsS -H "X-Spinnaker-User: ${PIPELINE_USER}" \
    "${GATE_URL}/applications/${APP_NAME}/pipelineConfigs" \
    | jq -r --arg n "$pname" '[.[] | select(.name == $n)][0].id // ""'
}

save_pipeline() {
  # $1 name ; $2 stages_json_array
  local pname="$1" stages="$2"
  local pid=""
  if pipeline_exists "${pname}"; then
    pid="$(get_pipeline_id "${pname}")"
  fi
  local payload
  if [ -n "$pid" ] && [ "$pid" != "null" ]; then
    payload=$(jq -n --arg app "$APP_NAME" --arg name "$pname" --arg id "$pid" --argjson stages "$stages" \
      '{application:$app, name:$name, id:$id, stages:$stages, limitConcurrent:true, keepWaitingPipelines:false}')
  else
    payload=$(jq -n --arg app "$APP_NAME" --arg name "$pname" --argjson stages "$stages" \
      '{application:$app, name:$name, stages:$stages, limitConcurrent:true, keepWaitingPipelines:false}')
  fi

  say "Salvando pipeline '${pname}' (POST /pipelines) ..."
  local code
  code=$(curl -sS -w "%{http_code}" -o /tmp/gate_resp.txt \
           -X POST -H "Content-Type: application/json" \
           -H "X-Spinnaker-User: ${PIPELINE_USER}" \
           -d "${payload}" \
           "${GATE_URL}/pipelines" || echo "000")
  if [ "${code}" != "200" ] && [ "${code}" != "202" ]; then
    err "Falha ao salvar pipeline '${pname}' (HTTP ${code})"
    echo "== Payload enviado =="; echo "${payload}" | jq .
    echo "== Resposta do Gate =="; cat /tmp/gate_resp.txt
    exit 1
  fi
  echo "OK (${code})"
}

create_one_pipeline() {
  # $1 env_code (env-a/env-b)
  local env_code="$1" title
  title="Compose $(pretty_env "$env_code") Up"
  say "Montando stages do pipeline '${title}' ..."
  local job_json delete_stage deploy_stage webhook_stage stages
  job_json="$(build_job_json "$env_code")"
  delete_stage="$(build_delete_stage_json "$env_code")"
  deploy_stage="$(build_deploy_stage_json "$env_code" "$job_json")"
  webhook_stage="$(build_webhook_stage_json "$env_code")"
  stages="$(jq -n --argjson d "$delete_stage" --argjson a "$deploy_stage" --argjson b "$webhook_stage" '[ $d, $a, $b ]')"
  save_pipeline "$title" "$stages"
}

delete_jobs_now() {
  say "Limpando Jobs antigos no namespace ${JOB_NAMESPACE} ..."
  kubectl -n "${JOB_NAMESPACE}" delete job compose-env-a-up --ignore-not-found || true
  kubectl -n "${JOB_NAMESPACE}" delete job compose-env-b-up --ignore-not-found || true
}

tips() {
  cat <<'TIP'
======== DICAS RÁPIDAS ========
• Ver pipelines:    http://localhost:8084/applications/demo-app/pipelineConfigs
• Disparar A:       curl -s -X POST "http://localhost:8084/pipelines/demo-app/Compose%20Env-a%20Up" -H "Content-Type: application/json" -H "X-Spinnaker-User: vanessa" -d '{}'
• Disparar B:       curl -s -X POST "http://localhost:8084/pipelines/demo-app/Compose%20Env-b%20Up" -H "Content-Type: application/json" -H "X-Spinnaker-User: vanessa" -d '{}'

Acompanhar execução:
  REF=$(curl -s -X POST "http://localhost:8084/pipelines/demo-app/Compose%20Env-a%20Up" \
        -H "Content-Type: application/json" -H "X-Spinnaker-User: vanessa" -d '{}' | jq -r .ref)
  while true; do
    curl -s "http://localhost:8084${REF}" -H "X-Spinnaker-User: vanessa" \
      | jq '{status, stages:[.stages[]|{name,type,status}]}' ; sleep 2
  done

Logs do Job:
  POD=$(kubectl -n ${JOB_NAMESPACE} get pod -l app=compose-env-a-up -o jsonpath='{.items[0].metadata.name}')
  kubectl -n ${JOB_NAMESPACE} describe pod "$POD" | sed -n '1,120p'
  kubectl -n ${JOB_NAMESPACE} logs "$POD" -c cli  --tail=200
  kubectl -n ${JOB_NAMESPACE} logs "$POD" -c dind --tail=200
TIP
}

main() {
  check_bin
  check_envs
  check_gate
  ensure_app
  apply_compose_configmaps
  delete_jobs_now          # <-- limpeza imediata no cluster
  create_one_pipeline "env-a"
  create_one_pipeline "env-b"

  say "Conferindo pipelines salvos:"
  curl -fsS -H "X-Spinnaker-User: ${PIPELINE_USER}" \
    "${GATE_URL}/applications/${APP_NAME}/pipelineConfigs" | jq -r '.[].name'

  tips
}

main "$@"   