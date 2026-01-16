#!/usr/bin/env bash
set -euo pipefail

# ===== Vars =====
NS="${JOB_NAMESPACE:-spinnaker}"
APP="${APP_NAME:-demo-app}"
GATE="${GATE_URL:-http://localhost:8084}"
USER="${PIPELINE_USER:-vanessa}"
PIPE_NAME="${PIPE_NAME:-Compose Env-a Up}"   # mude se necessário
HDR=(-H "X-Spinnaker-User: ${USER}")

say(){ echo -e ">> $*"; }
err(){ echo -e "!! $*" 1>&2; }

need(){ command -v "$1" >/dev/null 2>&1 || { err "Faltando '$1'"; exit 1; }; }
need jq
need curl
need kubectl

# ===== Wrappers que IGNORAM proxy para K8s e Gate =====
kctl() { env -u HTTPS_PROXY -u HTTP_PROXY -u https_proxy -u http_proxy -u NO_PROXY -u no_proxy kubectl "$@"; }
curl_nopxy() { env -u HTTPS_PROXY -u HTTP_PROXY -u https_proxy -u http_proxy -u NO_PROXY -u no_proxy curl --noproxy '*' "$@"; }

# ===== Funções auxiliares =====
urlenc() { python3 - "$@" <<'PY' 2>/dev/null || node -e "console.log(encodeURIComponent(process.argv[1]))" -- "$1"
import sys,urllib.parse; print(urllib.parse.quote(sys.argv[1]))
PY
}

diagnostico_proxy() {
  say "Diagnóstico de proxy (ambiente do shell):"
  echo "  HTTPS_PROXY=${HTTPS_PROXY-<unset>}"
  echo "  HTTP_PROXY=${HTTP_PROXY-<unset>}"
  echo "  NO_PROXY=${NO_PROXY-<unset>}"

  # Descobrir API server e checar se está no NO_PROXY
  local apiserver apihost
  apiserver="$(kctl config view --minify -o jsonpath='{.clusters[0].cluster.server}' 2>/dev/null || true)"
  if [[ -n "$apiserver" ]]; then
    apihost="$(echo "$apiserver" | sed -E 's~https?://([^:/]+).*~\1~')"
    echo "  Kubernetes API: $apiserver  (host: $apihost)"
    if [[ -n "${NO_PROXY-}" ]] && [[ ",$NO_PROXY," == *",$apihost,"* ]]; then
      echo "  ✔ $apihost está coberto no NO_PROXY"
    else
      echo "  ⚠ $apihost NÃO parece coberto no NO_PROXY"
      echo "    Sugestão: export NO_PROXY=\"${NO_PROXY-},$apihost\""
    fi
  else
    echo "  (Não foi possível obter o endpoint do API server)"
  fi
}

# ===== 0) Saúde/Gate e proxy =====
diagnostico_proxy
say "Gate: ${GATE}/health"
curl_nopxy -fsS "${GATE}/health" >/dev/null || { err "Gate indisponível"; exit 1; }
echo "OK"

# ===== 1) Buscar última execução do pipeline =====
say "Buscando execuções do pipeline '${PIPE_NAME}'..."
EXEC=$(
  curl_nopxy -fsS "${GATE}/applications/${APP}/pipelines?limit=50" "${HDR[@]}" \
  | jq -c --arg n "$PIPE_NAME" '[ .[] | select(.name==$n) ] | sort_by(.startTime // 0) | last // {}'
)
EXEC_ID=$(echo "$EXEC" | jq -r '.id // empty')
STATUS=$(echo "$EXEC" | jq -r '.status // empty')

if [[ -z "$EXEC_ID" ]]; then
  err "Nenhuma execução encontrada para '$PIPE_NAME'."
  say "Dica: dispare e rode de novo — POST ${GATE}/pipelines/${APP}/$(urlenc "$PIPE_NAME")"
  exit 1
fi

say "Última execução: $EXEC_ID  (status: ${STATUS})"
EXEC_URL="${GATE%/}/pipelines/${EXEC_ID}"
say "URL: $EXEC_URL"

say "Resumo de estágios:"
curl_nopxy -fsS "$EXEC_URL" "${HDR[@]}" \
| jq '{status, stages: [ .stages[] | {refId, name, type, status, startTime, endTime}] }'

# ===== 2) Detalhes/erros por estágio =====
say "Erros por estágio (se houver):"
curl_nopxy -fsS "$EXEC_URL" "${HDR[@]}" \
| jq -r '
  .stages[]
  | {name,type,status,
     err: (.context.exception.message
           // .context.failMessage
           // .context.error
           // .context.kato.tasks[0].exception
           // empty)}
  | select(.err!=null)
'

# ===== 3) Expression Evaluation (casos de "Failed to evaluate") =====
say "ExpressionEvaluationSummary (se existir):"
curl_nopxy -fsS "$EXEC_URL" "${HDR[@]}" \
| jq -r '[ .stages[] | select(.context.expressionEvaluationSummary!=null)
          | {stage:.name, expr: .context.expressionEvaluationSummary} ]'

# ===== 4) Manifest do Job que o Spinnaker tentou aplicar =====
say "Manifest do Job alvo (primeiro manifest do deploy):"
curl_nopxy -fsS "$EXEC_URL" "${HDR[@]}" \
| jq -c '( .stages[] | select(.type=="deployManifest") | .context.manifests[0] ) // empty' \
| tee /tmp/spin_job_manifest.json

JOB_NAME=$(jq -r '.metadata.name // empty' /tmp/spin_job_manifest.json 2>/dev/null || echo "")
if [[ -z "${JOB_NAME}" ]]; then
  say "Não foi possível extrair o nome do Job do contexto (talvez falhou antes do deploy)."
else
  say "Job alvo segundo o pipeline: ${JOB_NAME}"
fi

# ===== 5) Histórico do KatoTask (deployManifest) =====
say "Histórico do Kato (deploy):"
curl_nopxy -fsS "$EXEC_URL" "${HDR[@]}" \
| jq -r '( .stages[] | select(.type=="deployManifest") | .context["kato.tasks"][0].history[]?.status ) // "sem histórico"'

# ===== 6) Kubernetes: recursos/eventos/logs (sem proxy) =====
if [[ -n "${JOB_NAME}" ]]; then
  say "[K8s] get job/pods:"
  kctl -n "$NS" get job,pod -l "job-name=${JOB_NAME}" -o wide || true

  POD="$(kctl -n "$NS" get pod -l "job-name=${JOB_NAME}" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || true)"
  if [[ -n "${POD:-}" ]]; then
    say "[K8s] Logs do container CLI (últimos 200):"
    kctl -n "$NS" logs "$POD" -c cli --tail=200 || true
    say "[K8s] Logs do DIND (últimos 150):"
    kctl -n "$NS" logs "$POD" -c dind --tail=150 || true
  else
    say "[K8s] Nenhum Pod para o Job ainda."
  fi

  say "[K8s] Eventos recentes do namespace (tail 80):"
  # desabilitar paginação de eventos em clusters antigos
  kctl -n "$NS" get events --sort-by=.lastTimestamp | tail -n 80 || true
else
  say "[K8s] Pulando inspeção do Job (sem nome extraído)."
fi

# ===== 7) Clouddriver: logs recentes úteis =====
say "[Clouddriver] Últimos 300 logs, filtrando por job ou errors:"
kctl -n "$NS" logs deploy/spin-clouddriver --tail=300 \
  | egrep -i "${JOB_NAME:-compose-env-a-up}|KubernetesDeployManifestOperation|error|exception" -n || true

# ===== 8) Dicas finais =====
echo
say "DIAGNÓSTICO CONCLUÍDO"
cat <<'TIP'
• Se ainda aparecer “proxyconnect … lookup proxy”: seu kubectl está indo via proxy.
  - Adicione o host do API server ao NO_PROXY (veja o diagnóstico no topo).
  - Ou rode este script assim: (unset HTTPS_PROXY HTTP_PROXY https_proxy http_proxy; NO_PROXY="*" ./diag-compose-pipeline.sh)

• Se nos logs do container 'cli' você ver “Client sent an HTTP request to an HTTPS server” ao fazer docker pull:
  - Isso é proxy dentro do dind/daemon.
  - Reaplique o job de teste/pipeline com variáveis no Pod:
      HTTP_PROXY / HTTPS_PROXY (para ir à internet)
      NO_PROXY   (inclua hosts do cluster e registries internos)
      INSECURE_REGISTRY=host:port (se tiver registry HTTP)
TIP