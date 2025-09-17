#!/bin/bash
echo "🧨 Derrubando e removendo ambiente A..."

# Derruba e remove todos os containers e volumes do ambiente
docker-compose -f docker-compose.yaml down -v