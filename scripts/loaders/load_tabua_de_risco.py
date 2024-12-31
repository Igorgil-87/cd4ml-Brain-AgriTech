import pandas as pd
import logging

# Mapeamento completo das colunas
column_mapping = {
    "Nome_cultura": "nome_cultura",
    "SafraIni": "safra_ini",
    "SafraFin": "safra_fin",
    "Cod_Cultura": "cod_cultura",
    "Cod_Ciclo": "cod_ciclo",
    "Cod_Solo": "cod_solo",
    "geocodigo": "geocodigo",
    "UF": "uf",
    "municipio": "municipio",
    "Cod_Clima": "cod_clima",
    "Nome_Clima": "nome_clima",
    "Cod_Outros_Manejos": "cod_outros_manejos",
    "Nome_Outros_Manejos": "nome_outros_manejos",
    "Produtividade": "produtividade",
    "Cod_Munic": "cod_munic",
    "Cod_Meso": "cod_meso",
    "Cod_Micro": "cod_micro",
    "Portaria": "portaria",
    **{f"dec{i}": f"dec{i}" for i in range(1, 37)}  # Adicionar todos os decêntios
}


def load_tabua_de_risco(engine, csv_path = "/app/data/df_filtrado.csv" ):
    """
    Carrega os dados de um arquivo CSV para a tabela 'tabua_de_risco'.

    Args:
        csv_path (str): Caminho do arquivo CSV com os dados a serem carregados.
        engine (SQLAlchemy Engine): Conexão com o banco de dados.
        column_mapping (dict): Dicionário de mapeamento de colunas do CSV para o banco de dados.
    """
    try:
        # Log do início do processo
        logging.info(f"Iniciando o carregamento do arquivo CSV: {csv_path}")
        
        # Ler o CSV
        df = pd.read_csv(csv_path, sep=';', low_memory=False, encoding='latin1')

        # Renomear colunas para corresponder à tabela do banco de dados
        df.rename(columns=column_mapping, inplace=True)
     #   logging.info(f"Colunas detectadas e renomeadas: {df.columns.tolist()}")
        logging.info(f"Colunas detectadas e renomeadas")
        # Tratamento de dados
        for col in df.columns:
            if col.startswith('dec'):  # Converter decêntios para numérico
                df[col] = pd.to_numeric(df[col].replace(',', '.', regex=True), errors='coerce')
            elif col == 'safra_ini':  # Ajustar safra_ini para inteiro
                df[col] = pd.to_numeric(df[col], errors='coerce', downcast='integer')
            elif col in ['safra_fin', 'uf', 'municipio', 'nome_cultura', 'nome_clima', 'nome_outros_manejos', 'produtividade', 'portaria']:
                # Preencher valores nulos e limitar o comprimento
                df[col] = df[col].fillna("").astype(str).str.strip().str[:255]

        # Log da quantidade de linhas processadas
        logging.info(f"Total de linhas a serem carregadas: {len(df)}")

        # Inserir no banco de dados
        logging.info(f"Iniciando o carregamento para a tabela 'tabua_de_risco'...")
        with engine.begin() as connection:
            df.to_sql("tabua_de_risco", con=connection, if_exists='replace', index=False)
        logging.info(f"Carregamento do arquivo {csv_path} para a tabela 'tabua_de_risco' concluído com sucesso!")

    except Exception as e:
        logging.error(f"Erro ao carregar o arquivo {csv_path} na tabela 'tabua_de_risco': {e}")
        raise