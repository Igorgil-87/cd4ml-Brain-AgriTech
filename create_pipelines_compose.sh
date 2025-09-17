#!/usr/bin/env bash
set -euo pipefail

########################################
# CONFIG
########################################
GATE_ENDPOINT="${GATE_ENDPOINT:-http://localhost:8084}"
SPIN_USER="${SPIN_USER:-vanessa}"

APP_NAME="${APP_NAME:-demo-app}"
APP_EMAIL="${APP_EMAIL:-you@example.com}"

# Conta K8s (v2) configurada no Spinnaker
K8S_ACCOUNT="${K8S_ACCOUNT:-k8s-account}"
JOB_NAMESPACE="${JOB_NAMESPACE:-spinnaker}"

# Repositório com docker-compose
REPO_URL="${REPO_URL:-https://github.com/sua-org/seu-repo-compose.git}"
REPO_REF="${REPO_REF:-main}"

# Caminhos dos compose por ambiente
COMPOSE_FILE_A="${COMPOSE_FILE_A:-docker-compose.yml}"
COMPOSE_FILE_B="${COMPOSE_FILE_B:-docker-compose.yml}"

# Flags extras (-f override.yml, --profile, etc.)
COMPOSE_ARGS_A="${COMPOSE_ARGS_A:-}"
COMPOSE_ARGS_B="${COMPOSE_ARGS_B:-}"

# Disparar os pipelines após criar
TRIGGER_AFTER_CREATE="${TRIGGER_AFTER_CREATE:-false}"

########################################
# HELPERS
########################################
need() { command -v "$1" >/dev/null 2>&1 || { echo "Faltando '$1'"; exit 1; }; }
say()  { echo -e "\033[1;36m>> $*\033[0m"; }
err()  { echo -e "\033[1;31m!! $*\033[0m" >&2; }

json_escape() { python3 - <<'PY' "$1"
import json,sys; print(json.dumps(sys.argv[1]))
PY
}

########################################
# CHECKS
########################################
need curl; need jq; need python3
say "Verificando Gate em ${GATE_ENDPOINT}/health ..."
curl -sf "${GATE_ENDPOINT}/health" >/dev/null && echo "OK"

########################################
# CRIAR APLICAÇÃO VIA TASKS (ORCA)
########################################
create_app_if_needed() {
  local app="$1" email="$2"
  say "Garantindo aplicação '${app}' ..."
  if curl -sf -H "X-Spinnaker-User: ${SPIN_USER}" \
        "${GATE_ENDPOINT}/applications/${app}" >/dev/null; then
    echo "Aplicação já existe."
    return 0
  fi

  local body ref status
  body="$(cat <<JSON
{
  "job": [{
    "type": "createApplication",
    "application": {
      "name": "${app}",
      "email": "${email}",
      "cloudProviders": "kubernetes",
      "instancePort": 80,
      "trafficGuards": []
    }
  }],
  "application": "${app}",
  "description": "Create Application: ${app}"
}
JSON
)"
  say "Criando aplicação via /tasks ..."
  ref="$(curl -s -X POST "${GATE_ENDPOINT}/tasks" \
          -H "Content-Type: application/json" \
          -H "X-Spinnaker-User: ${SPIN_USER}" \
          -d "${body}" | jq -r .ref)"
  [[ -z "${ref}" || "${ref}" == "null" ]] && { err "Não recebi task ref"; exit 1; }
  echo "Task: ${ref}"

  while true; do
    status="$(curl -s -H "X-Spinnaker-User: ${SPIN_USER}" \
                  "${GATE_ENDPOINT}${ref}" | jq -r .status)"
    [[ "${status}" == "SUCCEEDED" ]] && { echo "Aplicação criada."; break; }
    [[ "${status}" == "TERMINAL"  ]] && { echo "WARN: task TERMINAL (talvez já existisse)"; break; }
    sleep 2
  done
}

########################################
# STAGE runJob (K8s v2) — DinD sidecar
########################################
make_runjob_stage_manifest() {
  local env_name="$1" compose_file="$2" compose_args="$3"
  local env_lc; env_lc="$(printf '%s' "${env_name}" | tr '[:upper:]' '[:lower:]')"

  local run_cmd="
set -e
apk add --no-cache git bash curl
mkdir -p /work && cd /work
git clone --depth=1 --branch ${REPO_REF} ${REPO_URL} src
cd src
for i in {1..60}; do
  if DOCKER_HOST=tcp://dind:2375 docker version >/dev/null 2>&1; then break; fi
  echo \"Aguardando dockerd... (\$i)\"; sleep 2
done
DOCKER_HOST=tcp://dind:2375 docker compose -f ${compose_file} ${compose_args} up -d
echo \"Compose ${env_name} concluído\"
"

  # Retorna um JSON de stage
  cat <<JSON
{
  "type": "runJob",
  "name": "Compose ${env_name} Up",
  "refId": "1",
  "requisiteStageRefIds": [],
  "cloudProvider": "kubernetes",
  "account": "${K8S_ACCOUNT}",
  "namespace": "${JOB_NAMESPACE}",
  "source": "text",
  "manifest": {
    "apiVersion": "batch/v1",
    "kind": "Job",
    "metadata": { "name": "compose-${env_lc}-up" },
    "spec": {
      "backoffLimit": 0,
      "template": {
        "metadata": { "labels": { "app": "compose-${env_lc}-up" } },
        "spec": {
          "restartPolicy": "Never",
          "containers": [
            {
              "name": "cli",
              "image": "docker:27-cli",
              "imagePullPolicy": "IfNotPresent",
              "env": [
                { "name": "DOCKER_HOST", "value": "tcp://dind:2375" }
              ],
              "command": [ "sh", "-lc", $(json_escape "$run_cmd") ]
            },
            {
              "name": "dind",
              "image": "docker:27-dind",
              "imagePullPolicy": "IfNotPresent",
              "securityContext": { "privileged": true },
              "args": ["--host=tcp://0.0.0.0:2375","--tls=false"]
            }
          ]
        }
      }
    }
  }
}
JSON
}

########################################
# CRIAR/ATUALIZAR PIPELINE
########################################
save_pipeline() {
  local pipeline_name="$1" env_name="$2" compose_file="$3" compose_args="$4"

  say "Salvando pipeline '${pipeline_name}' ..."
  local stage; stage="$(make_runjob_stage_manifest "${env_name}" "${compose_file}" "${compose_args}")"

  # Monta o payload do pipeline
  local payload
  payload="$(jq -n \
    --arg app "${APP_NAME}" \
    --arg name "${pipeline_name}" \
    --arg id  "${APP_NAME}-${pipeline_name}" \
    --argjson stages "[${stage}]" \
    '{
       application: $app,
       name: $name,
       id: $id,
       stages: $stages,
       triggers: [],
       expectedArtifacts: [],
       keepWaitingPipelines: false,
       limitConcurrent: true
     }'
  )"

  curl -s -X POST "${GATE_ENDPOINT}/pipelines" \
    -H "Content-Type: application/json" \
    -H "X-Spinnaker-User: ${SPIN_USER}" \
    -d "${payload}" >/dev/null

  echo "OK"
}

########################################
# DISPARAR PIPELINE (opcional)
########################################
trigger_pipeline() {
  local pipeline_name="$1"
  say "Disparando '${pipeline_name}' ..."
  curl -s -X POST "${GATE_ENDPOINT}/pipelines/${APP_NAME}/${pipeline_name}" \
      -H "Content-Type: application/json" \
      -H "X-Spinnaker-User: ${SPIN_USER}" \
      -d '{}' >/dev/null
  echo "OK"
}

########################################
# MAIN
########################################
create_app_if_needed "${APP_NAME}" "${APP_EMAIL}"

# Pipelines A e B (up -d via DinD)
save_pipeline "Compose A Up" "A" "${COMPOSE_FILE_A}" "${COMPOSE_ARGS_A}"
save_pipeline "Compose B Up" "B" "${COMPOSE_FILE_B}" "${COMPOSE_ARGS_B}"

say "Conferindo pipelines salvos:"
curl -s -H "X-Spinnaker-User: ${SPIN_USER}" \
  "${GATE_ENDPOINT}/applications/${APP_NAME}/pipelineConfigs" | jq '.[].name'

if [[ "${TRIGGER_AFTER_CREATE}" == "true" ]]; then
  trigger_pipeline "Compose A Up"
  trigger_pipeline "Compose B Up"
fi

cat <<EOF

======== DICAS RÁPIDAS ========
• Ver pipelines:    ${GATE_ENDPOINT}/applications/${APP_NAME}/pipelineConfigs
• Disparar A:       POST ${GATE_ENDPOINT}/pipelines/${APP_NAME}/Compose%20A%20Up  (body: {})
• Disparar B:       POST ${GATE_ENDPOINT}/pipelines/${APP_NAME}/Compose%20B%20Up  (body: {})

Ajustes comuns:
  - K8S_ACCOUNT / JOB_NAMESPACE
  - REPO_URL / REPO_REF
  - COMPOSE_FILE_A / COMPOSE_FILE_B
  - COMPOSE_ARGS_A / COMPOSE_ARGS_B (ex.: "-f docker-compose.yml -f docker-compose.a.yml --profile a")

Requisitos do cluster:
  - Conta K8s (v2) conectada ao Spinnaker.
  - Permitir privileged pods (para docker:dind).
  - Acesso ao repo (se privado, adapte o clone com auth).

EOF