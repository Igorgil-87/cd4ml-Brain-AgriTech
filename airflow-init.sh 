#!/bin/bash

echo "Esperando o PostgreSQL subir..."
while ! nc -z postgres 5432; do
  echo "Aguardando PostgreSQL em postgres:5432..."
  sleep 1
done

echo "Inicializando banco do Airflow..."
airflow db init

echo "Criando usuário admin..."
airflow users create \
  --username admin \
  --firstname Agro \
  --lastname User \
  --role Admin \
  --email admin@agro.com \
  --password admin123

echo "Finalizado!"