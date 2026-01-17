#!/usr/bin/env bash
set -euo pipefail

CTX="${1:-kind-spinnaker}"     # seu contexto kubectl
NS="${2:-cd4ml}"               # namespace separado (recomendado)
MANIFEST_DIR="${3:-k8s-out}"

log(){ echo "[$(date '+%F %T')] $*"; }
fail(){ echo "[$(date '+%F %T')] ERROR: $*" >&2; exit 1; }

command -v kubectl >/dev/null || fail "kubectl não encontrado"
kubectl config get-contexts "$CTX" >/dev/null 2>&1 || fail "Contexto kubectl não existe: $CTX"
[[ -d "$MANIFEST_DIR" ]] || fail "Diretório não existe: $MANIFEST_DIR"

log "Criando namespace $NS (se não existir)..."
kubectl --context "$CTX" get ns "$NS" >/dev/null 2>&1 || kubectl --context "$CTX" create ns "$NS"

log "Aplicando manifests de $MANIFEST_DIR em $NS..."
kubectl --context "$CTX" -n "$NS" apply -f "$MANIFEST_DIR"

log "Aguardando Deployments ficarem prontos (timeout 10m)..."
kubectl --context "$CTX" -n "$NS" wait --for=condition=available deploy --all --timeout=10m || true

log "Status geral:"
kubectl --context "$CTX" -n "$NS" get pods -o wide
kubectl --context "$CTX" -n "$NS" get svc
kubectl --context "$CTX" -n "$NS" get pvc

log "Se algo estiver CrashLoop, rode:"
log "  kubectl --context $CTX -n $NS describe pod <pod>"
log "  kubectl --context $CTX -n $NS logs <pod> --tail=200"
