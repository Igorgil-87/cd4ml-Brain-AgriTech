#!/usr/bin/env bash
set -euo pipefail

RENDERED="${1:-docker-compose.rendered.yml}"
OUT_DIR="${2:-k8s-out}"
JENKINS_SECRET_FILE="${3:-./jenkins/jenkins-admin-password.txt}"

log(){ echo "[$(date '+%F %T')] $*"; }
fail(){ echo "[$(date '+%F %T')] ERROR: $*" >&2; exit 1; }

command -v kompose >/dev/null || fail "kompose não encontrado. Instale: brew install kompose"
[[ -f "$RENDERED" ]] || fail "Não achei $RENDERED. Rode primeiro: ./00-render-compose.sh"

# Se o compose referencia secret por arquivo, o kompose PRECISA ler o arquivo
if [[ ! -f "$JENKINS_SECRET_FILE" ]]; then
  log "Secret do Jenkins não encontrado em $JENKINS_SECRET_FILE"
  log "Criando com valor default (troque depois): admin"
  mkdir -p "$(dirname "$JENKINS_SECRET_FILE")"
  printf "admin\n" > "$JENKINS_SECRET_FILE"
fi

mkdir -p "$OUT_DIR"
# limpa sem erro se vazio
rm -rf "${OUT_DIR:?}/"* 2>/dev/null || true

log "Convertendo com kompose..."
kompose convert -f "$RENDERED" --out "$OUT_DIR" --verbose

log "Arquivos gerados:"
ls -lha "$OUT_DIR" | head -n 80
