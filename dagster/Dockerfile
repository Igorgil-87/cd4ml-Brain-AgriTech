FROM python:3.10-slim

# Instala dependências básicas
RUN apt-get update && apt-get install -y gcc curl git

# Instala Dagster e Dagit
RUN pip install dagster dagit

# Define diretórios
ENV DAGSTER_HOME=/opt/dagster/dagster_home
WORKDIR /opt/dagster/app

COPY . /opt/dagster/app

CMD ["dagit", "-h", "0.0.0.0", "-p", "3000"]