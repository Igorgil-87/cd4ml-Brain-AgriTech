#!/bin/bash

echo "📁 Criando estrutura de DR local em cd4ml-brain-agritech ..."

mkdir -p dr-infra/env-a/config
mkdir -p dr-infra/env-b/config
mkdir -p dr-infra/spinnaker/pipelines
mkdir -p dr-infra/spinnaker/config
mkdir -p shared/models
mkdir -p shared/volumes
mkdir -p shared/data

touch dr-infra/env-a/docker-compose.yml
touch dr-infra/env-a/.env
touch dr-infra/env-a/config/spinnaker-config.yml

touch dr-infra/env-b/docker-compose.yml
touch dr-infra/env-b/.env
touch dr-infra/env-b/config/spinnaker-config.yml

touch dr-infra/spinnaker/pipelines/deploy-env-a.json
touch dr-infra/spinnaker/pipelines/deploy-env-b.json
touch dr-infra/spinnaker/config/halyard-config.yml

echo "✅ Estrutura DR criada com sucesso!"