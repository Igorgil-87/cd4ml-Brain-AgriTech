#!/usr/bin/env bash
set -euo pipefail

CTX="${1:-kind-spinnaker}"
NS="${2:-cd4ml}"

# ajuste portas se quiser
PORT_MLFLOW_LOCAL=12000
PORT_DAGSTER_LOCAL=3005
PORT_API_LOCAL=8000
PORT_UI_LOCAL=11001
PORT_MINIO_LOCAL=9000
PORT_PGADMIN_LOCAL=8081

echo "Port-forward (CTRL+C para parar)."
echo "MLflow   : http://localhost:${PORT_MLFLOW_LOCAL}"
echo "Dagster  : http://localhost:${PORT_DAGSTER_LOCAL}"
echo "API      : http://localhost:${PORT_API_LOCAL}"
echo "Interface: http://localhost:${PORT_UI_LOCAL}"
echo "MinIO    : http://localhost:${PORT_MINIO_LOCAL}"
echo "PgAdmin  : http://localhost:${PORT_PGADMIN_LOCAL}"

kubectl --context "$CTX" -n "$NS" port-forward svc/mlflow "${PORT_MLFLOW_LOCAL}:5000" &
kubectl --context "$CTX" -n "$NS" port-forward svc/dagster-webserver "${PORT_DAGSTER_LOCAL}:3000" &
kubectl --context "$CTX" -n "$NS" port-forward svc/cd4ml-api "${PORT_API_LOCAL}:8000" &
kubectl --context "$CTX" -n "$NS" port-forward svc/interface "${PORT_UI_LOCAL}:8000" &
kubectl --context "$CTX" -n "$NS" port-forward svc/minio "${PORT_MINIO_LOCAL}:9000" &
kubectl --context "$CTX" -n "$NS" port-forward svc/pgadmin "${PORT_PGADMIN_LOCAL}:80" &

wait
