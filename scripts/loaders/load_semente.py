import pandas as pd
import logging
import chardet


# Função para detectar codificação
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(10000))  # Detecta com base nos primeiros 10KB
        return result['encoding']



def load_semente(engine, file_path="/app/data/sementes.csv"):
    table_name = "semente"
    headers = ['produto', 'unidade', 'uf', 'ano', 'jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']

    try:
        # Detectar a codificação do arquivo
        encoding = detect_encoding(file_path)
        logging.info(f"Detectada a codificação do arquivo {file_path}: {encoding}")

        # Ler o arquivo CSV com delimitador correto
        df = pd.read_csv(
            file_path,
            sep=';',  # Ajustar para delimitador correto
            encoding=encoding,
            on_bad_lines='skip',  # Ignorar linhas problemáticas
            engine='python'
        )


        # Normalizar colunas
        df.columns = [col.strip().lower() for col in df.columns]

        # Validar e ajustar colunas
        missing_headers = [col for col in headers if col not in df.columns]
        if missing_headers:
            logging.error(f"Colunas ausentes no arquivo: {missing_headers}")
            return
        df = df[headers]

        # Limpar e converter valores numéricos
        numeric_columns = headers[4:]
        for col in numeric_columns:
            df[col] = df[col].astype(str).str.replace('.', '', regex=False)  # Remover separadores de milhares
            df[col] = df[col].astype(str).str.replace(',', '.', regex=False)  # Substituir vírgulas por pontos
            df[col] = df[col].str.strip()  # Remover espaços extras
            df[col] = pd.to_numeric(df[col], errors='coerce')  # Converter para float

        # Inserir os dados no banco
        with engine.begin() as connection:
            df.to_sql(table_name, con=connection, if_exists='append', index=False)
        logging.info(f"Tabela {table_name} carregada com sucesso!")
    
    except Exception as e:
        logging.error(f"Erro ao carregar a tabela {table_name}: {e}")