#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${1:-docker-compose.yaml}"
ENV_FILE="${2:-.env}"
RENDERED_OUT="${3:-docker-compose.rendered.yml}"

log(){ echo "[$(date '+%F %T')] $*"; }
fail(){ echo "[$(date '+%F %T')] ERROR: $*" >&2; exit 1; }

command -v docker >/dev/null || fail "docker não encontrado"
docker compose version >/dev/null 2>&1 || fail "docker compose não está disponível"

[[ -f "$COMPOSE_FILE" ]] || fail "Não achei $COMPOSE_FILE"
[[ -f "$ENV_FILE" ]] || fail "Não achei $ENV_FILE (crie com base no .env.example)"

# Validação mínima (sem expor secrets)
required_vars=(
  POSTGRES_DB POSTGRES_USER POSTGRES_PASSWORD
  MINIO_ACCESS_KEY MINIO_SECRET_KEY
  PGADMIN_DEFAULT_EMAIL PGADMIN_DEFAULT_PASSWORD
  API_KEY KAFKA_SERVER
  MLFLOW_TRACKING_URL MLFLOW_S3_ENDPOINT_URL
)

log "Validando variáveis essenciais em $ENV_FILE..."
missing=0
for v in "${required_vars[@]}"; do
  if ! grep -qE "^${v}=" "$ENV_FILE"; then
    echo " - faltando: $v"
    missing=1
  fi
done
[[ "$missing" -eq 0 ]] || fail "Faltam variáveis no $ENV_FILE"

log "Renderizando compose (docker compose config) -> $RENDERED_OUT"
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" config > "$RENDERED_OUT"

log "OK. Preview:"
head -n 25 "$RENDERED_OUT"
