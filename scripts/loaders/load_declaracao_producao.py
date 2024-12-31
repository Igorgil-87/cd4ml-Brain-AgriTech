import pandas as pd
from utils import engine, detect_encoding
import logging

def load_declaracao_producao(engine,file_path = "/app/data/sigefdeclaracaoareaproducao.csv"):
    
    table_name = "declaracao_producao"
    headers = ['tipo_periodo', 'periodo', 'area_total', 'municipio', 'uf', 'especie', 'cultivar', 'area_plantada', 'area_estimada', 'quant_reservada', 'data_plantio']

    try:
        encoding = detect_encoding(file_path)
        df = pd.read_csv(file_path, sep=',', encoding=encoding)

        # Normalizar colunas
        df.columns = [col.strip().lower() for col in df.columns]
        df = df[headers]

        # Converter valores
        df['area_total'] = pd.to_numeric(df['area_total'], errors='coerce')
        df['data_plantio'] = pd.to_datetime(df['data_plantio'], errors='coerce')

        # Inserir no banco
        with engine.begin() as connection:
            df.to_sql(table_name, con=connection, if_exists='append', index=False)

        logging.info(f"Tabela {table_name} carregada com sucesso!")
    except Exception as e:
        logging.error(f"Erro ao carregar a tabela {table_name}: {e}")