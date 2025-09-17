#!/usr/bin/env bash
set -euo pipefail

#############################################
# Spinnaker MPT v2 – Criar/Atualizar Template
# - Abre port-forward pro Front50 (svc/spin-front50)
# - POST (create) ou PUT (update) do template
# - Lista para confirmar
#############################################

# ---- Configuráveis via env/flag ----
NAMESPACE="${NAMESPACE:-spinnaker}"
FRONT50_LOCAL_PORT="${FRONT50_LOCAL_PORT:-18081}"
TEMPLATE_FILE="${TEMPLATE_FILE:-}"        # caminho do JSON do template (opcional)
TEMPLATE_ID_DEFAULT="pipelineTemplateA-v2" # usado no exemplo gerado
CLEANUP_PORT_FORWARD="${CLEANUP_PORT_FORWARD:-true}" # encerra pf ao sair

# ---- Parse flags simples ----
while [[ $# -gt 0 ]]; do
  case "$1" in
    -n|--namespace) NAMESPACE="$2"; shift 2 ;;
    -p|--port)      FRONT50_LOCAL_PORT="$2"; shift 2 ;;
    -f|--file)      TEMPLATE_FILE="$2"; shift 2 ;;
    -h|--help)
      cat <<EOF
Uso: $0 [-n spinnaker] [-p 18081] [-f template.json]

Sem -f, o script gera um template de exemplo (id: ${TEMPLATE_ID_DEFAULT}) com scopes=["global"].
Ambiente:
  NAMESPACE, FRONT50_LOCAL_PORT, TEMPLATE_FILE, CLEANUP_PORT_FORWARD
EOF
      exit 0
      ;;
    *)
      echo "Flag desconhecida: $1" >&2; exit 1 ;;
  esac
done

# ---- Checks básicos ----
for bin in kubectl curl jq; do
  command -v "$bin" >/dev/null 2>&1 || { echo "Dependência ausente: $bin"; exit 1; }
done

# ---- Funções auxiliares ----
pf_pid=""
cleanup() {
  if [[ "${CLEANUP_PORT_FORWARD}" == "true" && -n "${pf_pid}" ]]; then
    kill "${pf_pid}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

wait_for_http_up() {
  local url="$1" tries=40
  for i in $(seq 1 $tries); do
    if curl -fsS "$url" >/dev/null 2>&1; then return 0; fi
    sleep 0.5
  done
  return 1
}

# ---- Abre port-forward pro Front50 (svc/spin-front50:8080 -> localhost:FRONT50_LOCAL_PORT) ----
echo ">> Abrindo port-forward do Front50 em 127.0.0.1:${FRONT50_LOCAL_PORT} ..."
# Libera porta se estiver ocupada
if lsof -iTCP:"${FRONT50_LOCAL_PORT}" -sTCP:LISTEN -n -P >/dev/null 2>&1; then
  echo "   Porta ${FRONT50_LOCAL_PORT} está em uso. Tentando encerrar processos..."
  pids=$(lsof -t -iTCP:"${FRONT50_LOCAL_PORT}" -sTCP:LISTEN || true)
  [[ -n "${pids}" ]] && kill -9 $pids || true
fi

kubectl -n "${NAMESPACE}" port-forward svc/spin-front50 "${FRONT50_LOCAL_PORT}:8080" >/dev/null 2>&1 &
pf_pid=$!
sleep 0.5

echo ">> Aguardando Front50 responder em /health ..."
wait_for_http_up "http://127.0.0.1:${FRONT50_LOCAL_PORT}/health" \
  || { echo "Front50 não respondeu em /health"; exit 1; }

echo ">> Front50 OK."

# ---- Monta template (se não foi passado via -f) ----
if [[ -z "${TEMPLATE_FILE}" ]]; then
  TEMPLATE_FILE="$(mktemp -t mpt-template.XXXX).json"
  cat > "${TEMPLATE_FILE}" <<'EOF'
{
  "schema": "v2",
  "id": "pipelineTemplateA-v2",
  "metadata": {
    "name": "Pipeline Template Ambiente A",
    "description": "Template para deploy no ambiente A (com variável de conta)",
    "owner": "time-devops",
    "scopes": ["global"]
  },
  "variables": [
    { "name": "account", "type": "string", "defaultValue": "another-account" }
  ],
  "pipeline": {
    "stages": [
      {
        "id": "bake",
        "type": "bake",
        "cloudProviderType": "kubernetes",
        "name": "Bake manifest"
      },
      {
        "id": "deploy",
        "type": "deployManifest",
        "name": "Deploy Ambiente A",
        "account": "${ account }",
        "cloudProvider": "kubernetes",
        "manifestArtifactAccount": "embedded-artifact",
        "manifestArtifactId": "artifact"
      }
    ]
  }
}
EOF
  echo ">> Gerado template de exemplo em: ${TEMPLATE_FILE}"
fi

# ---- Descobre ID do template (pra PUT se já existir) ----
TEMPLATE_ID="$(jq -r '.id' "${TEMPLATE_FILE}")"
if [[ -z "${TEMPLATE_ID}" || "${TEMPLATE_ID}" == "null" ]]; then
  echo "ERRO: o JSON do template precisa ter um campo .id" >&2
  exit 1
fi

# ---- Tenta CREATE (POST). Se já existir, faz UPDATE (PUT). ----
echo ">> Publicando template '${TEMPLATE_ID}' no Front50 ..."
set +e
HTTP_CODE=$(curl -sS -o /dev/null -w "%{http_code}" \
  -H "Content-Type: application/json" \
  --data-binary @"${TEMPLATE_FILE}" \
  "http://127.0.0.1:${FRONT50_LOCAL_PORT}/v2/pipelineTemplates")
set -e

case "${HTTP_CODE}" in
  200|201)
    echo "   POST ok (${HTTP_CODE})."
    ;;
  409)
    echo "   Já existe (409). Tentando UPDATE (PUT) ..."
    curl -sS -X PUT \
      -H "Content-Type: application/json" \
      --data-binary @"${TEMPLATE_FILE}" \
      "http://127.0.0.1:${FRONT50_LOCAL_PORT}/v2/pipelineTemplates/${TEMPLATE_ID}" >/dev/null
    echo "   PUT ok."
    ;;
  *)
    echo "   POST retornou HTTP ${HTTP_CODE}. Saindo."
    exit 1
    ;;
esac

# ---- Lista para confirmar ----
echo ">> Templates no Front50:"
curl -s "http://127.0.0.1:${FRONT50_LOCAL_PORT}/v2/pipelineTemplates" | jq '.'

echo ">> Concluído com sucesso."