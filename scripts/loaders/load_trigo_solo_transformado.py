import pandas as pd
import logging
import chardet
# Função para detectar codificação
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(10000))  # Detecta com base nos primeiros 10KB
        return result['encoding']

def load_trigo_solo_transformado(engine, file_path="/app/data/raw_data/rendimento/trigosolo_transformado.csv"):
    table_name = "trigo_solo_transformado"
    headers = {
        "Safra": "safra", "Cultura": "cultura", "UF": "uf", "Município": "municipio",
        "Grupo": "grupo", "Solo": "solo", "Outros manejos": "outros_manejos",
        "Clima": "clima", "Decênio": "decenio", "Valor": "valor", "Data": "data"
    }

    try:
        encoding = detect_encoding(file_path)
        logging.info(f"Encoding trigo_solo_transformado {encoding} encontrado com sucesso!")  

        # Processar em partes
        chunksize = 10000  # Ajuste conforme necessário
        for chunk in pd.read_csv(file_path, sep=',', encoding=encoding, chunksize=chunksize):
            # Renomear colunas
            chunk.rename(columns=headers, inplace=True)

            # Inserir no banco
            with engine.begin() as connection:
                chunk.to_sql(table_name, con=connection, if_exists='append', index=False)

        logging.info(f"Tabela {table_name} carregada com sucesso!")
    except Exception as e:
        logging.error(f"Erro ao carregar a tabela {table_name}: {e}")
    
    table_name = "trigo_solo_transformado"
    headers = {
        "Safra": "safra", "Cultura": "cultura", "UF": "uf", "Município": "municipio",
        "Grupo": "grupo", "Solo": "solo", "Outros manejos": "outros_manejos",
        "Clima": "clima", "Decênio": "decenio", "Valor": "valor", "Data": "data"
    }

    try:
        encoding = detect_encoding(file_path)
        logging.info(f"Encoding trigo_solo_transformado {encoding} encontrado com sucesso!")          
        df = pd.read_csv(file_path, sep=',', encoding=encoding)

        # Renomear colunas
        df.rename(columns=headers, inplace=True)

        # Inserir no banco
        with engine.begin() as connection:
            df.to_sql(table_name, con=connection, if_exists='append', index=False)

        logging.info(f"Tabela {table_name} carregada com sucesso!")
    except Exception as e:
        logging.error(f"Erro ao carregar a tabela {table_name}: {e}")