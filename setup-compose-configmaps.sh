#!/usr/bin/env bash
# Cria/atualiza os ConfigMaps para env-a e env-b usando os arquivos dentro de dr-infra/.
# Execute a partir da RAIZ do projeto (onde existe a pasta dr-infra/).
# Uso:
#   ./setup-compose-configmaps.sh                  # aplica A e B
#   ./setup-compose-configmaps.sh --only a         # só A
#   ./setup-compose-configmaps.sh --only b         # só B
#   ./setup-compose-configmaps.sh --trigger        # também dispara os pipelines no Gate
#   JOB_NAMESPACE=outro-namespace ./setup-compose-configmaps.sh

set -euo pipefail

say(){ echo ">> $*"; }
err(){ echo "!! $*" 1>&2; }
need(){ command -v "$1" >/dev/null 2>&1 || { err "Faltando '$1'"; exit 1; }; }

# ===================== Config =====================
NS="${JOB_NAMESPACE:-spinnaker}"
ROOT="${PROJECT_ROOT:-$PWD}"

COMPOSE_A="${PATH_COMPOSE_A:-$ROOT/dr-infra/env-a/docker-compose.yaml}"
ENV_A="${ENV_FILE_A:-$ROOT/dr-infra/env-a/.env}"

COMPOSE_B="${PATH_COMPOSE_B:-$ROOT/dr-infra/env-b/docker-compose.yaml}"
ENV_B="${ENV_FILE_B:-$ROOT/dr-infra/env-b/.env}"

# Disparo opcional de pipeline
GATE_URL="${GATE_URL:-http://localhost:8084}"
APP_NAME="${APP_NAME:-demo-app}"
PIPELINE_USER="${PIPELINE_USER:-vanessa}"

ONLY=""
TRIGGER="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --only)    ONLY="${2:-}"; shift 2;;
    --trigger) TRIGGER="true"; shift;;
    -h|--help)
      cat <<EOF
Uso: $0 [--only a|b] [--trigger]
Vars úteis:
  JOB_NAMESPACE     (default: spinnaker)
  PROJECT_ROOT      (default: diretório atual)
  PATH_COMPOSE_A    (override do caminho)
  ENV_FILE_A        (override do caminho)
  PATH_COMPOSE_B    (override do caminho)
  ENV_FILE_B        (override do caminho)
  GATE_URL, APP_NAME, PIPELINE_USER
EOF
      exit 0;;
    *) err "Flag desconhecida: $1"; exit 1;;
  esac
done

check_bins(){
  need kubectl
  command -v curl >/dev/null 2>&1 || true
  command -v jq >/dev/null 2>&1 || true
}

check_layout(){
  [[ -d "$ROOT/dr-infra" ]] || { err "Não achei dr-infra/ em: $ROOT"; exit 1; }
  if [[ -z "$ONLY" || "$ONLY" == "a" ]]; then
    [[ -f "$COMPOSE_A" ]] || { err "Arquivo não encontrado: $COMPOSE_A"; exit 1; }
    [[ -f "$ENV_A" ]] || say "Aviso: .env de A não encontrado (criaremos CM vazio)"
  fi
  if [[ -z "$ONLY" || "$ONLY" == "b" ]]; then
    [[ -f "$COMPOSE_B" ]] || { err "Arquivo não encontrado: $COMPOSE_B"; exit 1; }
    [[ -f "$ENV_B" ]] || say "Aviso: .env de B não encontrado (criaremos CM vazio)"
  fi
}

apply_cm(){
  # $1=a|b  $2=compose_path  $3=env_path
  local code="$1" compose_path="$2" env_path="$3"
  local cm_yaml="compose-yaml-$code"
  local cm_env="compose-env-$code"

  say "Aplicando ConfigMap $cm_yaml ..."
  kubectl -n "$NS" create configmap "$cm_yaml" \
    --from-file=docker-compose.yaml="$compose_path" \
    --dry-run=client -o yaml | kubectl apply -f -

  if [[ -f "$env_path" ]]; then
    say "Aplicando ConfigMap $cm_env (com .env) ..."
    kubectl -n "$NS" create configmap "$cm_env" \
      --from-file=.env="$env_path" \
      --dry-run=client -o yaml | kubectl apply -f -
  else
    say "Aplicando ConfigMap $cm_env (vazio) ..."
    kubectl -n "$NS" create configmap "$cm_env" \
      --from-literal=.env= \
      --dry-run=client -o yaml | kubectl apply -f -
  fi

  kubectl -n "$NS" get cm "$cm_yaml" "$cm_env" -o wide
}

trigger_pipeline(){
  # $1=a|b
  local code="$1" title
  [[ "$code" == "a" ]] && title="Compose Env-a Up" || title="Compose Env-b Up"

  if ! command -v curl >/dev/null 2>&1; then
    say "curl não disponível — pulando trigger ($title)."
    return 0
  fi

  # URL encode seguro sem depender de python: usa jq se existir
  local enc_title="$title"
  if command -v jq >/dev/null 2>&1; then
    enc_title=$(jq -nr --arg s "$title" '$s|@uri')
  else
    # fallback simples (espaço -> %20)
    enc_title="${title// /%20}"
  fi

  local url="${GATE_URL}/pipelines/${APP_NAME}/${enc_title}"
  say "Disparando pipeline: $title"
  local http
  http=$(curl -sS -w "%{http_code}" -o /tmp/trigger_${code}.json \
        -X POST -H "Content-Type: application/json" -H "X-Spinnaker-User: ${PIPELINE_USER}" \
        -d '{}' "$url" || echo "000")
  if [[ "$http" == "200" || "$http" == "202" ]]; then
    say "OK (HTTP $http)."
    [[ -s /tmp/trigger_${code}.json ]] && (command -v jq >/dev/null 2>&1 && jq . /tmp/trigger_${code}.json || cat /tmp/trigger_${code}.json)
  else
    err "Falha (HTTP $http) ao chamar $url"
    [[ -s /tmp/trigger_${code}.json ]] && cat /tmp/trigger_${code}.json || true
  fi
}

main(){
  check_bins

  if [[ -n "$ONLY" && "$ONLY" != "a" && "$ONLY" != "b" ]]; then
    err "--only deve ser 'a' ou 'b'"; exit 1;
  fi

  say "Namespace: $NS"
  say "Projeto:   $ROOT"
  check_layout

  if [[ -z "$ONLY" || "$ONLY" == "a" ]]; then
    apply_cm "a" "$COMPOSE_A" "$ENV_A"
  fi
  if [[ -z "$ONLY" || "$ONLY" == "b" ]]; then
    apply_cm "b" "$COMPOSE_B" "$ENV_B"
  fi

  cat <<EOF

======== DICAS ========
• Ver ConfigMaps:
    kubectl -n "$NS" get cm compose-yaml-a compose-env-a
    kubectl -n "$NS" get cm compose-yaml-b compose-env-b

• Eventos recentes (debug):
    kubectl -n "$NS" get events --sort-by=.lastTimestamp | tail -n 50

• Disparar pipelines manualmente:
    curl -s -X POST "$GATE_URL/pipelines/$APP_NAME/Compose%20Env-a%20Up" -H "Content-Type: application/json" -H "X-Spinnaker-User: $PIPELINE_USER" -d '{}'
    curl -s -X POST "$GATE_URL/pipelines/$APP_NAME/Compose%20Env-b%20Up" -H "Content-Type: application/json" -H "X-Spinnaker-User: $PIPELINE_USER" -d '{}'
=======================

EOF

  if [[ "$TRIGGER" == "true" ]]; then
    trigger_pipeline "a"
    trigger_pipeline "b"
  fi

  say "Concluído."
}

main "$@"