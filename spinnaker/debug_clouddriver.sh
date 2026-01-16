#!/usr/bin/env bash
set -euo pipefail

NS="${NS:-spinnaker}"

log() { printf '\n==== %s ====\n' "$*"; }

log "1) Conferindo namespace: $NS"
kubectl get ns "$NS" >/dev/null

log "2) Descobrindo pods"
kubectl -n "$NS" get pod -l cluster=spin-clouddriver -o name | head -n1 | cut -d/ -f2 > /tmp/CLD_POD || true
kubectl -n "$NS" get pod -l cluster=spin-orca        -o name | head -n1 | cut -d/ -f2 > /tmp/ORCA_POD || true

CLD_POD="$(cat /tmp/CLD_POD 2>/dev/null || true)"
ORCA_POD="$(cat /tmp/ORCA_POD 2>/dev/null || true)"

echo "Clouddriver POD: ${CLD_POD:-<não encontrado>}"
echo "Orca POD       : ${ORCA_POD:-<não encontrado>}"

if [[ -z "${CLD_POD:-}" ]]; then
  echo "ERRO: não achei pod do clouddriver (label cluster=spin-clouddriver)."
  exit 1
fi
if [[ -z "${ORCA_POD:-}" ]]; then
  echo "AVISO: não achei pod do orca (label cluster=spin-orca). Sigo sem o teste do Orca."
fi

log "3) Dentro do Clouddriver: checando porta 7002 e /health"
kubectl -n "$NS" exec -it "$CLD_POD" -- sh -lc 'ss -ltn 2>/dev/null | grep :7002 || netstat -ltn 2>/dev/null | grep :7002 || echo "nada ouvindo em 7002"'
kubectl -n "$NS" exec -it "$CLD_POD" -- sh -lc 'wget -qO- http://127.0.0.1:7002/health || echo FAIL'

log "4) Ajustando Service spin-clouddriver (selector + publishNotReadyAddresses)"
kubectl -n "$NS" patch svc spin-clouddriver --type merge \
  -p '{"spec":{"selector":{"cluster":"spin-clouddriver"},"publishNotReadyAddresses":true}}' >/dev/null || true

log "5) Endpoints do Service"
kubectl -n "$NS" get svc spin-clouddriver -o wide
kubectl -n "$NS" get endpoints spin-clouddriver -o wide || true
kubectl -n "$NS" get endpointslice -l kubernetes.io/service-name=spin-clouddriver -o wide || true

if [[ -n "${ORCA_POD:-}" ]]; then
  log "6) Do lado do Orca → HTTP para spin-clouddriver:7002/health"
  kubectl -n "$NS" exec -it "$ORCA_POD" -- sh -lc 'wget -qO- http://spin-clouddriver.spinnaker:7002/health || echo FAIL'
fi

log "7) Dica: se 7002 não estiver ouvindo, force as envs do clouddriver e recomece"
cat <<'TIP'
kubectl -n spinnaker set env deploy/spin-clouddriver \
  JAVA_TOOL_OPTIONS="-Dserver.address=0.0.0.0 -Dserver.port=7002" \
  SERVER_ADDRESS=0.0.0.0 SERVER_PORT=7002
kubectl -n spinnaker rollout restart deploy/spin-clouddriver
kubectl -n spinnaker rollout status deploy/spin-clouddriver
TIP