import pandas as pd
import logging
import chardet


# Configurar o log
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Função para detectar a codificação
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(10000))  # Detecta com base nos primeiros 10KB
        return result['encoding']

def load_producao_fertilizantes(engine,file_path = "/app/data/FERTILIZANTES.csv"):
    
    table_name = "producao_fertilizantes"
    headers = ['produto', 'unidade', 'uf', 'ano', 'jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']

    try:
        encoding = detect_encoding(file_path)
        df = pd.read_csv(file_path, sep=';', encoding=encoding)

        # Normalizar colunas
        df.columns = [col.strip().lower() for col in df.columns]
        df = df[headers]

        # Converter valores numéricos
        numeric_columns = headers[4:]
        for col in numeric_columns:
            df[col] = df[col].str.replace(',', '.').astype(float)

        # Inserir no banco
        with engine.begin() as connection:
            df.to_sql(table_name, con=connection, if_exists='append', index=False)

        logging.info(f"Tabela {table_name} carregada com sucesso!")
    except Exception as e:
        logging.error(f"Erro ao carregar a tabela {table_name}: {e}")