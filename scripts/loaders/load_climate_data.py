import pandas as pd
import logging
from sqlalchemy import create_engine
import os


def process_climate_data(file_path, engine):
    try:
        # Detectar codificação do arquivo
        encoding = detect_encoding(file_path)
        logging.info(f"Detectada a codificação do arquivo {file_path}: {encoding}")

        # Ler o arquivo CSV
        df = pd.read_csv(file_path, sep=";", encoding=encoding, skiprows=8)


        # Renomear colunas
        df.rename(columns=column_mapping_clima, inplace=True)


        # Converter colunas numéricas para o formato correto
        numeric_columns = [
            'precipitacao_total_mm', 'pressao_atm_estacao_mb', 'pressao_atm_max_mb',
            'pressao_atm_min_mb', 'radiacao_global_kj', 'temp_bulbo_seco_c',
            'temp_orvalho_c', 'temp_max_c', 'temp_min_c', 'temp_orvalho_max_c',
            'temp_orvalho_min_c', 'vento_rajada_max', 'vento_velocidade'
        ]
        df = clean_numeric_columns(df, numeric_columns)

        # Converter colunas específicas
        df["data"] = pd.to_datetime(df["data"], errors="coerce")
        df["hora_utc"] = df["hora_utc"].astype(str)

        # Remover linhas com datas inválidas
        df.dropna(subset=["data"], inplace=True)
        df["data"] = df["data"].dt.strftime("%Y-%m-%d")

        # Garantir que a tabela exista no banco
        ensure_table_exists("climate_data", engine)

        # Validar e inserir os dados no banco
        logging.info(f"Validando e inserindo dados na tabela 'climate_data'...")
        map_and_insert_to_table(df, "climate_data", engine)

    except Exception as e:
        logging.error(f"Erro ao processar arquivo {file_path}: {e}")

def clean_numeric_columns(df, columns):
    """
    Limpa e converte colunas numéricas, substituindo vírgulas por pontos e
    tratando valores não numéricos como NaN.
    """
    for col in columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '.', regex=False).str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce')  # Converte para float, substituindo valores inválidos por NaN
    return df


def handle_missing_values(df):
    """
    Substitui valores ausentes por padrões aceitáveis.
    """
    fill_values = {
        "vento_velocidade": 0.0,
        "vento_direcao_grados": 0.0,
        "vento_rajada_max": 0.0,
        "precipitacao_total_mm": 0.0,
        "pressao_atm_estacao_mb": 1013.25,  # Valor padrão médio
        "radiacao_global_kj": 0.0,
    }
    return df.fillna(value=fill_values)


def map_and_insert_to_table(df, table_name, engine):
    """Mapeia as colunas do DataFrame para as colunas da tabela no banco de dados
    e insere os dados na tabela.
    
    Args:
        df (pd.DataFrame): DataFrame contendo os dados.
        table_name (str): Nome da tabela no banco de dados.
        engine (sqlalchemy.Engine): Conexão com o banco de dados.
    """
    # Conectar ao banco para buscar informações sobre a tabela
    with engine.connect() as conn:
        result = conn.execute(
            f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '{table_name}';
            """
        )
        table_columns = {row['column_name'] for row in result.fetchall()}
    
    # Filtrar colunas do DataFrame que existem na tabela
    mapped_columns = [col for col in df.columns if col in table_columns]
    df_mapped = df[mapped_columns]
    
    # Garantir que as colunas ausentes sejam preenchidas com NULL
    for col in table_columns - set(mapped_columns):
        df_mapped[col] = None  # Adicionar colunas ausentes com valor NULL
    
    # Ordenar as colunas do DataFrame para combinar com a tabela
    df_mapped = df_mapped[[col for col in table_columns if col in df_mapped.columns]]
    
    # Inserir os dados na tabela
    try:
        df_mapped.to_sql(table_name, engine, if_exists='append', index=False)
        logging.info(f"Dados inseridos com sucesso na tabela '{table_name}'.")
    except Exception as e:
        logging.error(f"Erro ao inserir dados na tabela '{table_name}': {e}")


def validate_dataframe(df, table_name, engine):
    """
    Valida o DataFrame antes da inserção no banco de dados.

    Args:
        df (pd.DataFrame): DataFrame a ser validado.
        table_name (str): Nome da tabela no banco de dados.
        engine (SQLAlchemy Engine): Conexão com o banco de dados.

    Returns:
        bool: True se a validação for bem-sucedida, False caso contrário.
    """
    try:
        # Obter as colunas da tabela no banco de dados
        with engine.connect() as connection:
            db_columns = pd.read_sql(f"SELECT * FROM {table_name} LIMIT 0", connection).columns

        # Verificar se todas as colunas do DataFrame estão no banco
        missing_columns = [col for col in db_columns if col not in df.columns]
        if missing_columns:
            logging.error(f"Colunas ausentes no DataFrame para a tabela {table_name}: {missing_columns}")
            return False

        # Verificar tipos de dados para compatibilidade
        with engine.connect() as connection:
            table_info = pd.read_sql(f"""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = '{table_name}';
            """, connection)

        column_types = {row["column_name"]: row["data_type"] for _, row in table_info.iterrows()}
        for col in df.columns:
            if col in column_types:
                expected_type = column_types[col]
                actual_type = str(df[col].dtype)
                if not is_type_compatible(actual_type, expected_type):
                    logging.warning(f"Tipo incompatível para coluna '{col}'. "
                                    f"Esperado: {expected_type}, Encontrado: {actual_type}.")
            else:
                logging.warning(f"Coluna '{col}' encontrada no DataFrame, mas não está na tabela '{table_name}'.")

        # Verificar se o DataFrame está vazio
        if df.empty:
            logging.error(f"O DataFrame para a tabela {table_name} está vazio.")
            return False

        # Validação concluída com sucesso
        logging.info(f"Validação do DataFrame para a tabela {table_name} foi bem-sucedida.")
        return True

    except Exception as e:
        logging.error(f"Erro ao validar DataFrame para a tabela {table_name}: {e}")
        return False


def is_type_compatible(actual_type, expected_type):
    """
    Verifica se o tipo do dado no DataFrame é compatível com o tipo esperado no banco de dados.

    Args:
        actual_type (str): Tipo real do dado no DataFrame.
        expected_type (str): Tipo esperado no banco de dados.

    Returns:
        bool: True se os tipos forem compatíveis, False caso contrário.
    """
    # Mapear tipos esperados para simplificar a verificação
    type_mapping = {
        "text": ["object", "string"],
        "double precision": ["float64", "float32", "int64", "int32"],
        "integer": ["int64", "int32"],
        "numeric": ["float64", "float32"],
        "timestamp without time zone": ["datetime64[ns]"]
    }

    for db_type, pandas_types in type_mapping.items():
        if expected_type == db_type and actual_type in pandas_types:
            return True

    return False



def detect_encoding(file_path):
    """
    Detecta a codificação do arquivo CSV.
    """
    import chardet
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(10000))  # Detecta com base nos primeiros 10KB
        return result['encoding']


# Função para Processar Vários Arquivos
def load_climate_data(engine, base_path="/app/data/clima"):
    files = [os.path.join(base_path, f) for f in os.listdir(base_path) if f.endswith(".CSV")]
    for file in files:
        try:
            process_climate_data(file, engine)
        except Exception as e:
            logging.error(f"Erro ao processar arquivo {file}: {e}")



def ensure_table_exists(table_name, engine):
    """
    Garante que a tabela existe no banco de dados. Se não existir, cria a tabela.
    """
    try:
        with engine.connect() as connection:
            # Verificar se a tabela existe
            result = connection.execute(f"""
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = '{table_name}'
                );
            """).scalar()

            if not result:
                logging.info(f"Tabela '{table_name}' não encontrada. Criando a tabela...")
                create_table_sql = """
                CREATE TABLE public.climate_data (
                    data TEXT,
                    hora_utc TEXT,
                    precipitacao_total_mm DOUBLE PRECISION,
                    pressao_atm_estacao_mb DOUBLE PRECISION,
                    pressao_atm_max_mb DOUBLE PRECISION,
                    pressao_atm_min_mb DOUBLE PRECISION,
                    radiacao_global_kj DOUBLE PRECISION,
                    temp_bulbo_seco_c DOUBLE PRECISION,
                    temp_orvalho_c DOUBLE PRECISION,
                    temp_max_c DOUBLE PRECISION,
                    temp_min_c DOUBLE PRECISION,
                    temp_orvalho_max_c DOUBLE PRECISION,
                    temp_orvalho_min_c DOUBLE PRECISION,
                    umidade_rel_max DOUBLE PRECISION,
                    umidade_rel_min DOUBLE PRECISION,
                    umidade_rel DOUBLE PRECISION,
                    vento_direcao_grados DOUBLE PRECISION,
                    vento_rajada_max DOUBLE PRECISION,
                    vento_velocidade DOUBLE PRECISION
                );
                """
                connection.execute(create_table_sql)
                logging.info(f"Tabela '{table_name}' criada com sucesso.")

    except Exception as e:
        logging.error(f"Erro ao verificar/criar a tabela '{table_name}': {e}")
        raise


# Mapeamento das colunas do arquivo de clima
column_mapping_clima = {
    "Data": "data",
    "Hora UTC": "hora_utc",
    "PRECIPITAÇÃO TOTAL, HORÁRIO (mm)": "precipitacao_total_mm",
    "PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)": "pressao_atm_estacao_mb",
    "PRESSÃO ATMOSFERICA MAX.NA HORA ANT. (AUT) (mB)": "pressao_atm_max_mb",
    "PRESSÃO ATMOSFERICA MIN. NA HORA ANT. (AUT) (mB)": "pressao_atm_min_mb",
    "RADIACAO GLOBAL (Kj/m²)": "radiacao_global_kj",
    "TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)": "temp_bulbo_seco_c",
    "TEMPERATURA DO PONTO DE ORVALHO (°C)": "temp_orvalho_c",
    "TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)": "temp_max_c",
    "TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)": "temp_min_c",
    "TEMPERATURA ORVALHO MAX. NA HORA ANT. (AUT) (°C)": "temp_orvalho_max_c",
    "TEMPERATURA ORVALHO MIN. NA HORA ANT. (AUT) (°C)": "temp_orvalho_min_c",
    "UMIDADE REL. MAX. NA HORA ANT. (AUT) (%)": "umidade_rel_max",
    "UMIDADE REL. MIN. NA HORA ANT. (AUT) (%)": "umidade_rel_min",
    "UMIDADE RELATIVA DO AR, HORARIA (%)": "umidade_rel",
    "VENTO, DIREÇÃO HORARIA (gr) (° (gr))": "vento_direcao_grados",
    "VENTO, RAJADA MAXIMA (m/s)": "vento_rajada_max",
    "VENTO, VELOCIDADE HORARIA (m/s)": "vento_velocidade",
}