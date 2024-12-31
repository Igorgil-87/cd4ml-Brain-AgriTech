import pandas as pd
import logging
import chardet

def detect_encoding(file_path):
    """
    Detecta a codificação do arquivo CSV.
    """
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(10000))  # Detecta com base nos primeiros 10KB
        return result['encoding']







def load_fertilizantes(engine, file_path="/app/data/FERTILIZANTES.csv"):
    table_name = "producao_fertilizantes"
    headers = ['produto', 'unidade', 'uf', 'ano', 'jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']

    try:
        # Detectar a codificação do arquivo
        encoding = detect_encoding(file_path)
        logging.info(f"Detectada a codificação do arquivo {file_path}: {encoding}")

        # Ler o arquivo CSV com o separador correto
        df = pd.read_csv(
            file_path,
            sep=';',  # Ajustado para o separador correto
            encoding=encoding,
            on_bad_lines='skip',  # Ignorar linhas problemáticas
            engine='python'
        )

        logging.info(f"Primeiras linhas do DataFrame:\n{df.head()}")

        # Normalizar colunas
        df.columns = [col.strip().lower() for col in df.columns]

        # Validar e ajustar colunas para os headers esperados
        missing_headers = [col for col in headers if col not in df.columns]
        if missing_headers:
            logging.error(f"Colunas ausentes no arquivo: {missing_headers}")
            return
        df = df[headers]

        # Converter valores numéricos
        numeric_columns = headers[4:]
        for col in numeric_columns:
            df[col] = df[col].astype(str).str.replace(',', '.').astype(float)

        # Inserir no banco
        with engine.begin() as connection:
            df.to_sql(table_name, con=connection, if_exists='append', index=False)

        logging.info(f"Tabela {table_name} carregada com sucesso!")
    except Exception as e:
        logging.error(f"Erro ao carregar a tabela {table_name}: {e}")



 