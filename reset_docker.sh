#!/bin/bash

echo "🚫 Parando todos os containers..."
docker ps -aq | xargs -r docker stop

echo "🧹 Removendo todos os containers..."
docker ps -aq | xargs -r docker rm

echo "🧨 Removendo todos os volumes (dados serão perdidos)..."
docker volume ls -q | xargs -r docker volume rm

echo "🧯 Removendo todas as imagens..."
docker images -q | xargs -r docker rmi -f

echo "🔌 Removendo rede 'jenkins_nw' se existir..."
docker network ls | grep jenkins_nw | awk '{print $1}' | xargs -r docker network rm

echo "🛠️  Subindo novamente com docker-compose --build..."
docker-compose up --build