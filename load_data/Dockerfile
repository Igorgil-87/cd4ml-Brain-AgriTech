# Define a imagem base com Python 3.9
FROM python:3.9-slim

# Instala as dependências do sistema
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Configura o PYTHONPATH para que os módulos sejam corretamente localizados
#ENV PYTHONPATH=/app/scripts
ENV PYTHONPATH=/app
# Copia o arquivo de dependências e instala as bibliotecas Python
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r /tmp/requirements.txt

# Copia os scripts e os dados para o contêiner
COPY scripts /app/scripts
COPY data /app/data

# Adiciona logs para depuração da estrutura
RUN ls -l /app/scripts && ls -l /app/scripts/loaders && ls -l /app/data


# Define o comando padrão para executar o script de carga
ENTRYPOINT ["python", "/app/scripts/load_data.py"]