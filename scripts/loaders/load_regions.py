import pandas as pd
import logging
import chardet


# Função para detectar codificação
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(10000))  # Detecta com base nos primeiros 10KB
        return result['encoding']

def load_regions(engine,file_path = "/app/data/estados.csv"):
    
    table_name = "regions"
    headers = ['cod', 'nome', 'sigla', 'regiao']

    try:
        encoding = detect_encoding(file_path)
        df = pd.read_csv(file_path, sep=',', encoding=encoding)

        # Normalizar colunas
        df.columns = [col.strip().lower() for col in df.columns]
        df = df[headers]

        # Inserir no banco
        with engine.begin() as connection:
            df.to_sql(table_name, con=connection, if_exists='append', index=False)

        logging.info(f"Tabela {table_name} carregada com sucesso!")
    except Exception as e:
        logging.error(f"Erro ao carregar a tabela {table_name}: {e}")