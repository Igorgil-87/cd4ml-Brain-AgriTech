import pandas as pd
import chardet
import logging
from sqlalchemy import create_engine

# Configurar o log
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Função para detectar a codificação
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(10000))  # Detecta com base nos primeiros 10KB
        return result['encoding']

def load_agrotoxico(engine, file_path="/app/data/AGROTOXICO.csv"):
    table_name = "agrotoxico"
    headers = ['produto', 'unidade', 'uf', 'ano', 'jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']

    try:
        # Detectar a codificação do arquivo
        encoding = detect_encoding(file_path)
        logging.info(f"Detectada a codificação do arquivo {file_path}: {encoding}")

        # Ler o arquivo CSV
        df = pd.read_csv(
            file_path,
            sep=';',  # Ajuste o delimitador
            encoding=encoding,
            on_bad_lines='warn',
            engine='python'
        )

        # Normalizar colunas
        df.columns = [col.strip().lower() for col in df.columns]

        # Validar e ajustar colunas para os headers esperados
        if not set(headers).issubset(df.columns):
            missing_headers = [col for col in headers if col not in df.columns]
            logging.error(f"Colunas ausentes no arquivo: {missing_headers}")
            return

        df = df[headers]

        # Converter valores numéricos
        numeric_columns = headers[4:]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '.').astype(float)

        # Inserir no banco
        with engine.connect() as connection:
            df.to_sql(table_name, con=connection, if_exists='append', index=False)

        logging.info(f"Tabela {table_name} carregada com sucesso!")

    except Exception as e:
        logging.error(f"Erro ao carregar a tabela {table_name}: {e}")