# Define a imagem base
FROM python:3.9-slim

# Instala as dependências do sistema
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Copia as dependências do Python e instala
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copia os scripts e os dados
COPY scripts /app/scripts
COPY data /app/data

# Comando padrão para executar o script
CMD ["python", "/app/scripts/load_data.py"]