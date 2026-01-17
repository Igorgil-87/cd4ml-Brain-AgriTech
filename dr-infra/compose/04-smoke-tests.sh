#!/usr/bin/env bash
set -euo pipefail

MLFLOW_URL="${1:-http://localhost:12000}"
API_URL="${2:-http://localhost:8000}"

echo "[SMOKE] MLflow experiments..."
curl -sS "${MLFLOW_URL}/api/2.0/mlflow/experiments/list" | head -c 300; echo

echo "[SMOKE] API health (ajuste se tiver endpoint específico)..."
curl -sS "${API_URL}/" | head -c 300; echo
