#!/bin/bash

# Caminho onde estão os pipelines JSON
PIPELINES_DIR="dr-infra/spinnaker/pipelines"

# URL do Gate do Spinnaker
GATE_URL="http://localhost:8084"

# Itera sobre os arquivos JSON
for file in "$PIPELINES_DIR"/*.json; do
    echo "Importando pipeline: $file"
    curl -X POST "$GATE_URL/pipelines" \
        -H "Content-Type: application/json" \
        --data-binary "@$file"
    echo ""
done