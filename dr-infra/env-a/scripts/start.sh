#!/bin/bash
set -e

echo "[ENV-A] 🟢 Inicializando ambiente A via docker-compose..."
docker-compose -f ./dr-infra/env-a/docker-compose.yaml up -d --remove-orphans

echo "[ENV-A] ⏳ Aguardando containers ficarem saudáveis..."
watch -n 5 "docker ps --filter name=env-a"

echo "[ENV-A] ✅ Ambiente A ativo com sucesso!"

### 📁 Arquivo: dr-infra/env-a/scripts/destroy.sh
#!/bin/bash
set -e

echo "[ENV-A] 🛑 Removendo ambiente A..."
docker-compose -f ./dr-infra/env-a/docker-compose.yaml down -v --remove-orphans

echo "[ENV-A] ✅ Ambiente A destruído com sucesso."