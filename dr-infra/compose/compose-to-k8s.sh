#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="./logs"
OUT_DIR="./k8s-out"
COMPOSE_IN="./docker-compose.yaml"
COMPOSE_RENDERED="./docker-compose.rendered.yml"

mkdir -p "$LOG_DIR" "$OUT_DIR"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }
fail() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $*" >&2; exit 1; }

log "Validando pré-requisitos..."
command -v docker >/dev/null 2>&1 || fail "docker não encontrado"
docker compose version >/dev/null 2>&1 || fail "docker compose não encontrado"
command -v kompose >/dev/null 2>&1 || fail "kompose não encontrado (brew install kompose)"

log "Checando arquivo compose: $COMPOSE_IN"
[[ -f "$COMPOSE_IN" ]] || fail "Não achei $COMPOSE_IN no diretório atual: $(pwd)"

log "Renderizando compose (expande envs/anchors) -> $COMPOSE_RENDERED"
docker compose -f "$COMPOSE_IN" config > "$COMPOSE_RENDERED" 2> "$LOG_DIR/docker-compose-config.err" \
  || fail "Falhou em 'docker compose config'. Veja $LOG_DIR/docker-compose-config.err"

log "Limpando saída antiga em $OUT_DIR"
rm -rf "$OUT_DIR"/*

log "Convertendo com kompose -> $OUT_DIR"
kompose convert -f "$COMPOSE_RENDERED" --out "$OUT_DIR" --verbose \
  > "$LOG_DIR/kompose.out" 2> "$LOG_DIR/kompose.err" || fail "Kompose falhou. Veja $LOG_DIR/kompose.err"

log "Arquivos gerados:"
ls -lha "$OUT_DIR" | sed -n '1,120p'

COUNT=$(find "$OUT_DIR" -maxdepth 1 -type f -name "*.yaml" -o -name "*.yml" | wc -l | tr -d ' ')
if [[ "$COUNT" == "0" ]]; then
  fail "Kompose não gerou manifests. Veja $LOG_DIR/kompose.out e $LOG_DIR/kompose.err"
fi

log "OK ✅ Kompose gerou $COUNT manifest(s) em $OUT_DIR"
log "Próximo passo: ajustar secrets/volumes/healthchecks e aplicar no kind."
