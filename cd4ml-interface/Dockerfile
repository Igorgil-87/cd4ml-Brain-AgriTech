FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia apenas o requirements.txt e instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# O restante do código será montado via volume
# (não precisa dar COPY . . pois o volume sobrescreve)

EXPOSE 8000

# Usa flask ou python main.py, ambos funcionam
CMD ["python", "main.py"]