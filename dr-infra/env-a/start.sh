#!/bin/bash
echo "🚀 Iniciando ambiente A..."

# Verifica se já está rodando
if docker-compose -f docker-compose.yaml ps | grep -q "Up"; then
  echo "⚠️ Ambiente A já está em execução."
  exit 0
fi

# Sobe os serviços
docker-compose -f docker-compose.yaml up -d

# Aguarda até os serviços ficarem prontos
echo "⏳ Aguardando serviços ficarem saudáveis..."
./check_health.sh