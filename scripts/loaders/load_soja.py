import pandas as pd
import logging
import chardet


# Função para detectar codificação
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(10000))  # Detecta com base nos primeiros 10KB
        return result['encoding']


def load_soja(engine, file_path="/app/data/soja.csv"):
    table_name = "soja"
    headers = ['localidade', 'unidade', 'jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']
    numeric_columns = headers[2:]

    try:
        # Log do início do processo
        logging.info(f"Iniciando o carregamento do arquivo CSV: {table_name}")

        # Detectar codificação e ler o arquivo
        encoding = detect_encoding(file_path)
        logging.info(f"Encoding soja {encoding} encontrado com sucesso!")        
        df = pd.read_csv(file_path, sep=';', encoding=encoding)

        # Log das colunas encontradas
        logging.info(f"Colunas encontradas no arquivo: {list(df.columns)}")

        # Normalizar colunas do CSV
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

        # Verificar se todas as colunas necessárias estão presentes
        missing_columns = [col for col in headers if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Colunas ausentes no arquivo CSV: {missing_columns}")

        # Selecionar apenas as colunas esperadas
        df = df[headers]

        # Tratar valores numéricos
        for col in numeric_columns:
            df[col] = df[col].astype(str).str.replace(',', '.').str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Inserir no banco de dados
        with engine.begin() as connection:
            df.to_sql(table_name, con=connection, if_exists='append', index=False)

        logging.info(f"Tabela {table_name} carregada com sucesso!")

    except Exception as e:
        logging.error(f"Erro ao carregar a tabela {table_name}: {e}")