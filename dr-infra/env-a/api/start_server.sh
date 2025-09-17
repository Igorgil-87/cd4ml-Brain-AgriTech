#!/usr/bin/env bash
set -euo pipefail

# ===================== Config =====================
APP_MOD="env_a_api:app"
HOST="0.0.0.0"
PORT="${PORT:-18081}"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "${SCRIPT_DIR}"

VENV_DIR=".venv"
LOG_DIR=".logs"
API_LOG="${LOG_DIR}/api.log"
NGROK_LOG="${LOG_DIR}/ngrok.log"
PUB_URL_FILE="${LOG_DIR}/public_url.txt"

REQ_FILE="requirements.txt"     # fastapi, uvicorn[standard], pydantic, pyyaml
NGROK_BIN="${NGROK_BIN:-$(command -v ngrok || true)}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
UVICORN_BIN="${UVICORN_BIN:-${VENV_DIR}/bin/uvicorn}"

# ===================== Utils ======================
log()  { echo -e "🔹 $*"; }
ok()   { echo -e "✅ $*"; }
warn() { echo -e "⚠️  $*" >&2; }
err()  { echo -e "❌ $*" >&2; }

ensure_logs() {
  mkdir -p "${LOG_DIR}"
  : > "${NGROK_LOG}"
  touch "${API_LOG}" "${PUB_URL_FILE}"
}

have() { command -v "$1" >/dev/null 2>&1; }

venv_activate() {
  if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
    log "Criando virtualenv ${VENV_DIR}…"
    "${PYTHON_BIN}" -m venv "${VENV_DIR}"
  fi
  # shellcheck disable=SC1090
  source "${VENV_DIR}/bin/activate"
}

install_requirements() {
  log "Instalando requirements…"
  pip install --upgrade pip >/dev/null 2>&1 || true
  if [[ -f "${REQ_FILE}" ]]; then
    pip install -r "${REQ_FILE}"
  else
    warn "requirements.txt não encontrado — instalando deps mínimas"
    pip install fastapi "uvicorn[standard]" pydantic pyyaml
  fi
}

wait_http() {
  local url="$1" tries="${2:-30}" sleep_s="${3:-1}"
  local i=0
  until curl -fsS --max-time 1 "$url" >/dev/null 2>&1; do
    (( i++ >= tries )) && return 1
    sleep "$sleep_s"
  done
  return 0
}

port_busy() {
  lsof -nP -iTCP:"$1" -sTCP:LISTEN >/dev/null 2>&1
}

pid_by_pattern() {
  pgrep -f "$1" || true
}

kill_by_pattern() {
  local pat="$1"
  pkill -f "$pat" >/dev/null 2>&1 || true
}

# ===================== API ====================
api_up() {
  ensure_logs
  venv_activate
  install_requirements

  # Se já está respondendo, não reinicia
  if wait_http "http://127.0.0.1:${PORT}/status" 3 0.5; then
    ok "API já está ok: http://127.0.0.1:${PORT}/status"
    return 0
  fi

  log "Subindo API (${APP_MOD}) na porta ${PORT}…"

  # Evita matar outra coisa: só processos compatíveis
  local pat="${UVICORN_BIN} ${APP_MOD} --host ${HOST} --port ${PORT}"
  local pids
  pids="$(pid_by_pattern "${pat}")"
  if [[ -n "${pids}" ]]; then
    warn "Encontradas instâncias antigas, finalizando…"
    kill ${pids} >/dev/null 2>&1 || true
    sleep 0.5
  fi

  # Se a porta ficou ocupada por algo estranho, avisa
  if port_busy "${PORT}"; then
    err "A porta ${PORT} já está em uso por outro processo. Libere-a e tente novamente."
    lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN || true
    exit 1
  fi

  # Sobe o Uvicorn em background, com PYTHONPATH correto
  # shellcheck disable=SC2086
  nohup env PYTHONPATH="." "${UVICORN_BIN}" ${APP_MOD} --host "${HOST}" --port "${PORT}" \
    >> "${API_LOG}" 2>&1 &

  # Espera até 90s
  if wait_http "http://127.0.0.1:${PORT}/status" 90 1; then
    ok "API ok: http://127.0.0.1:${PORT}/status"
  else
    err "API não respondeu — veja ${API_LOG}"
    tail -n 200 "${API_LOG}" || true
    exit 1
  fi
}

# ===================== NGROK ====================
ngrok_up() {
  if [[ -z "${NGROK_BIN}" ]]; then
    warn "ngrok não encontrado (https://ngrok.com/download) — seguindo sem túnel."
    return 0
  fi

  # Se dashboard já está ativo, tenta reaproveitar
  if curl -fsS http://127.0.0.1:4040/api/tunnels >/dev/null 2>&1; then
    local existing
    existing="$(curl -fsS http://127.0.0.1:4040/api/tunnels \
      | "${PYTHON_BIN}" - <<'PY'
import sys, json
t=json.load(sys.stdin).get("tunnels",[])
t=[x for x in t if x.get("proto")=="https"]
print(t[0]["public_url"] if t else "")
PY
    )"
    if [[ -n "${existing}" ]]; then
      ok "Túnel existente: ${existing}"
      echo "${existing}" > "${PUB_URL_FILE}"
      return 0
    fi
  fi

  log "Abrindo ngrok…"
  # Mata ngrok apontando pra essa porta
  kill_by_pattern "${NGROK_BIN} http 127.0.0.1:${PORT}" || true
  : > "${NGROK_LOG}"

  nohup "${NGROK_BIN}" http "127.0.0.1:${PORT}" --log=stdout \
    > "${NGROK_LOG}" 2>&1 &

  # Espera dashboard subir
  if ! wait_http "http://127.0.0.1:4040/api/tunnels" 30 0.5; then
    err "dashboard do ngrok não respondeu — veja ${NGROK_LOG}"
    exit 1
  fi

  local pub
  pub="$(curl -fsS http://127.0.0.1:4040/api/tunnels \
    | "${PYTHON_BIN}" - <<'PY'
import sys, json
t=json.load(sys.stdin).get("tunnels",[])
t=[x for x in t if x.get("proto")=="https"]
print(t[0]["public_url"] if t else "")
PY
  )"

  if [[ -n "${pub}" ]]; then
    echo "${pub}" > "${PUB_URL_FILE}"
    ok "Túnel público: ${pub}"
    echo "Exemplos:"
    echo "  curl -fsS ${pub}/status | jq"
    echo "  curl -fsS -X POST ${pub}/start -H 'Content-Type: application/json' -H 'X-EnvA-Token: fake-token-123' -d '{\"env\":\"env-a\",\"app\":\"cd4ml-api\"}' | jq"
  else
    err "Não consegui obter a URL pública — veja ${NGROK_LOG}"
    exit 1
  fi
}

# ===================== Comandos ====================
cmd_up()    { api_up; ngrok_up; }
cmd_down()  {
  log "Encerrando ngrok e API…"
  kill_by_pattern "${NGROK_BIN} http 127.0.0.1:${PORT}" || true
  kill_by_pattern "${UVICORN_BIN} ${APP_MOD} --host ${HOST} --port ${PORT}" || true
  sleep 0.3
  ok "Encerrado."
}
cmd_status(){
  echo "— API —"
  if curl -fsS "http://127.0.0.1:${PORT}/status" >/dev/null 2>&1; then
    ok "API respondendo em http://127.0.0.1:${PORT}/status"
  else
    warn "API não respondeu"
  fi
  echo "— ngrok —"
  if [[ -f "${PUB_URL_FILE}" && -s "${PUB_URL_FILE}" ]]; then
    ok "Último túnel: $(cat "${PUB_URL_FILE}")"
  else
    if curl -fsS http://127.0.0.1:4040/api/tunnels >/dev/null 2>&1; then
      local pub="$(curl -fsS http://127.0.0.1:4040/api/tunnels \
        | "${PYTHON_BIN}" - <<'PY'
import sys, json
t=json.load(sys.stdin).get("tunnels",[])
t=[x for x in t if x.get("proto")=="https"]
print(t[0]["public_url"] if t else "")
PY
      )"
      [[ -n "${pub}" ]] && ok "Túnel atual: ${pub}" || warn "Dashboard ok, mas sem túnel HTTPS ativo"
    else
      warn "Sem túnel e dashboard do ngrok inativo"
    fi
  fi
}
cmd_logs()  {
  echo "=== ${API_LOG} ==="
  [[ -f "${API_LOG}" ]] && tail -n 200 "${API_LOG}" || echo "(sem logs)"
  echo
  echo "=== ${NGROK_LOG} ==="
  [[ -f "${NGROK_LOG}" ]] && tail -n 200 "${NGROK_LOG}" || echo "(sem logs)"
}

usage() {
  cat <<EOF
uso: $0 [up|down|status|logs]
  up     - sobe API + túnel ngrok (imprime URL pública)
  down   - derruba ambos
  status - checa saúde da API e túnel
  logs   - mostra últimos logs (API e ngrok)
EOF
}

main() {
  ensure_logs
  local cmd="${1:-up}"
  case "$cmd" in
    up)     cmd_up ;;
    down)   cmd_down ;;
    status) cmd_status ;;
    logs)   cmd_logs ;;
    *) usage; exit 1 ;;
  esac
}

main "$@"