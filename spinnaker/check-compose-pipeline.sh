#!/usr/bin/env bash
# Verifica Gate/credenciais, encontra pipeline por nome, dispara, captura REF,
# acompanha estágios e confere Job/Pod/logs do compose env-a.

set -euo pipefail

# ===== Config / Defaults =====
NS="${JOB_NAMESPACE:-spinnaker}"
APP="${APP_NAME:-demo-app}"
GATE="${GATE_URL:-http://localhost:8084}"
USER="${PIPELINE_USER:-vanessa}"
PIPE_NAME="${PIPE_NAME:-Compose Env-a Up}"   # ajuste se o nome for outro

hdr_ct=(-H "Content-Type: application/json")
hdr_user=(-H "X-Spinnaker-User: ${USER}")

say(){ echo ">> $*"; }
err(){ echo "!! $*" 1>&2; }

# URL-encode sem depender de Python
urlencode() {
  # shellcheck disable=SC2018,SC2019
  local s="$1" out="" c
  for ((i=0;i<${#s};i++)); do
    c="${s:i:1}"
    case "$c" in
      [a-zA-Z0-9.~_-]) out+="$c" ;;
      ' ') out+='%20' ;;
      *) printf -v out '%s%%%02X' "$out" "'$c" ;;
    esac
  done
  printf '%s' "$out"
}

cleanup() {
  [[ -n "${watch_pid:-}" ]] && kill "$watch_pid" >/dev/null 2>&1 || true
}
trap cleanup EXIT

need() { command -v "$1" >/dev/null 2>&1 || { err "Faltando binário: $1"; exit 1; }; }

# ===== 0) Checagens básicas =====
need curl
need jq
need kubectl
# yq é opcional (para status yaml), se não existir caímos no kubectl -o wide
if ! command -v yq >/dev/null 2>&1; then
  say "Aviso: 'yq' não encontrado; status do Job será mostrado em modo 'wide'."
fi

say "Gate health: ${GATE}/health"
curl -fsS "${GATE}/health" >/dev/null && echo "OK" || { err "Gate indisponível"; exit 1; }

say "Credenciais visíveis:"
curl -fsS "${GATE}/credentials" | jq -r '.[].name' | sed 's/^/  - /'

# ===== 1) Conferir pipelines da app =====
say "Listando pipelines da app '${APP}'..."
cfg_json=$(curl -fsS "${GATE}/applications/${APP}/pipelineConfigs")
echo "$cfg_json" | jq -r '.[].name' | sed 's/^/  - /'

# Checar existência exata
if ! echo "$cfg_json" | jq -e --arg n "$PIPE_NAME" '.[] | select(.name==$n)' >/dev/null; then
  err "Pipeline não encontrado com nome EXATO: \"$PIPE_NAME\""
  say "Dicas:"
  echo "  - Verifique espaços/maiúsculas/minúsculas."
  echo "  - Rode assim: PIPE_NAME='Nome exato' ./check-compose-pipeline.sh"
  exit 1
fi

PIPE_ID=$(echo "$cfg_json" | jq -r --arg n "$PIPE_NAME" '[.[] | select(.name==$n)][0].id // ""')
say "Pipeline OK. ID: ${PIPE_ID:-<sem id>}  Nome: $PIPE_NAME"

# ===== 2) Disparar pipeline (captura robusta do REF) =====
say "Disparando pipeline por nome..."
resp_all=$(mktemp)
enc_name=$(urlencode "$PIPE_NAME")
http_code=$(curl -sS -i -w "\n%{http_code}\n" -o "$resp_all" \
  -X POST "${GATE}/pipelines/${APP}/${enc_name}" "${hdr_ct[@]}" "${hdr_user[@]}" -d '{}' | tail -n1)

say "HTTP: $http_code"
if [[ "$http_code" != "200" && "$http_code" != "202" ]]; then
  err "Disparo falhou (HTTP $http_code). Corpo/headers abaixo:"
  sed -n '1,200p' "$resp_all"
  exit 1
fi

# Tentar extrair REF do corpo (parte depois dos headers)
REF=$(awk 'BEGIN{b=0} /^$/{b=1;next} {if(b==1) print}' "$resp_all" | jq -r 'try .ref // ""' 2>/dev/null || echo "")
if [[ -z "${REF}" ]]; then
  # Tentar pelo Location dos headers
  REF=$(grep -i '^Location:' "$resp_all" | awk '{print $2}' | tr -d '\r\n')
  if [[ -n "$REF" && "$REF" != http* ]]; then
    REF="${GATE%/}${REF}"
  fi
fi

if [[ -z "${REF}" ]]; then
  err "Não foi possível extrair REF do corpo nem do Location."
  say "Resposta completa:"
  sed -n '1,200p' "$resp_all"
  exit 1
fi
say "REF: $REF"

# ===== 3) Acompanhar pipeline (status + estágios) =====
say "Acompanhando pipeline (CTRL+C para sair): status + estágios"
while true; do
  curl -fsS "${REF}" "${hdr_user[@]}" \
    | jq '{status, stages:[.stages[]|{name,type,status}]}' || true
  sleep 5
done &
watch_pid=$!

# ===== 4) Aguardar o Job e mostrar logs =====
say "Aguardando Job do compose env-a aparecer (até 120s)..."
for _ in {1..60}; do
  if kubectl -n "$NS" get job compose-env-a-up >/dev/null 2>&1; then
    echo "Job encontrado."
    break
  fi
  sleep 2
done

if ! kubectl -n "$NS" get job compose-env-a-up >/dev/null 2>&1; then
  err "Job compose-env-a-up NÃO apareceu no namespace ${NS}."
  say "Veja o pipeline em ${REF} e logs do Clouddriver:"
  echo "kubectl -n \"$NS\" logs deploy/spin-clouddriver --tail=200 | grep -i -E 'compose-env-a-up|error|exception' -n"
  exit 1
fi

say "Esperando Pod do Job ficar disponível..."
kubectl -n "$NS" get job,pod -l job-name=compose-env-a-up -o wide || true

# Capturar POD
POD=""
for _ in {1..60}; do
  POD=$(kubectl -n "$NS" get pod -l job-name=compose-env-a-up -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || true)
  [[ -n "${POD:-}" ]] && break
  sleep 2
done
[[ -z "${POD:-}" ]] && { err "Pod do Job não surgiu."; exit 1; }

say "Pod: $POD"
say "Logs do container CLI (docker compose):"
kubectl -n "$NS" logs "$POD" -c cli --tail=200 || true

say "Logs do DIND:"
kubectl -n "$NS" logs "$POD" -c dind --tail=120 || true

# ===== 5) Status final do Job =====
say "Status do Job:"
if command -v yq >/dev/null 2>&1; then
  kubectl -n "$NS" get job compose-env-a-up -o yaml | yq '.status'
else
  kubectl -n "$NS" get job compose-env-a-up -o wide
fi

say "Pronto. Para encerrar o watcher do pipeline: CTRL+C (se ainda estiver rodando)."