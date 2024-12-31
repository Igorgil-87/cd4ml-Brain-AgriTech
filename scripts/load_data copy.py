import pandas as pd
from sqlalchemy import create_engine
import psycopg2
import csv
import logging
import os
import glob
import re
from datetime import datetime
import warnings
import chardet


warnings.filterwarnings("ignore", category=DeprecationWarning)

# Configuração do banco de dados
DB_CONFIG = {
    "database": "brain_agro",
    "user": "agro_user",
    "password": "agro_password",
    "host": "postgres",  # Ajuste o host para "localhost" ou outro, conforme necessário
    "port": "5432"
}

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Criação da string de conexão SQLAlchemy
connection_string = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(connection_string)

# Testa conexão e verifica tabelas
try:
    with engine.connect() as connection:
        result = connection.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
        tables = [row[0] for row in result]
        logging.info(f"Tabelas disponíveis no banco: {tables}")
except Exception as e:
    logging.error(f"Erro ao conectar e verificar tabelas: {e}")
    raise

# Chaves obrigatórias para validação de metadados
required_keys = ["REGIAO", "UF", "ESTACAO", "CODIGO (WMO)", "LATITUDE", "LONGITUDE", "ALTITUDE", "DATA DE FUNDACAO"]


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

# Função para carregar CSV para a tabela
def load_csv_to_table(file_path, table_name, headers):
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(file_path):
            logging.error(f"Arquivo {file_path} não encontrado.")
            return

        # Detectar codificação e delimitador
        encoding = detect_encoding(file_path)
        delimiter = detect_delimiter(file_path, encoding)
        logging.info(f"Detectada a codificação '{encoding}' e delimitador '{delimiter}' no arquivo {file_path}")

        # Ler o arquivo CSV
        df = pd.read_csv(file_path, sep=delimiter, encoding=encoding, low_memory=False)

        # Normalizar cabeçalhos do arquivo para corresponder à tabela
        df.columns = [col.strip().lower().replace(" ", "_").replace("ã", "a").replace("ç", "c") for col in df.columns]
        logging.info(f"Colunas detectadas no arquivo {file_path}: {df.columns.tolist()}")

        # Renomear cabeçalhos do arquivo para corresponder ao banco de dados
        column_mapping = dict(zip(df.columns, headers))
        df.rename(columns=column_mapping, inplace=True)

        # Verificar se todos os cabeçalhos obrigatórios estão presentes
        missing_headers = [header for header in headers if header not in df.columns]
        if missing_headers:
            logging.error(f"O arquivo {file_path} está faltando os cabeçalhos obrigatórios: {missing_headers}")
            return

        # Selecionar somente as colunas necessárias
        df = df[headers]

        # Tratar valores numéricos e datas
        for col in headers:
            if col in ['area_total', 'area_plantada', 'area_estimada', 'quant_reservada']:
                df[col] = pd.to_numeric(df[col].replace(',', '.', regex=True), errors='coerce')
            elif col == 'data_plantio':
                df[col] = pd.to_datetime(df[col], errors='coerce')

        # Inserir os dados no banco de dados
        logging.info(f"Carregando dados do arquivo {file_path} na tabela {table_name}...")
        with engine.begin() as connection:
            df.to_sql(table_name, con=connection, if_exists='append', index=False)
        logging.info(f"Dados do arquivo {file_path} carregados com sucesso na tabela {table_name}!")

    except Exception as e:
        logging.error(f"Erro ao carregar o arquivo {file_path} na tabela {table_name}: {e}")

def clean_and_load_filtered_csv(csv_path, table_name, column_mapping):
    """Limpa e carrega o CSV filtrado no banco de dados."""
    try:
        logging.info(f"Lendo o arquivo CSV filtrado: {csv_path}")
        df = pd.read_csv(csv_path, sep=';', low_memory=False, encoding='latin1')

        # Renomear colunas para corresponder à tabela do banco de dados
        df.rename(columns=column_mapping, inplace=True)

        # Tratamento de dados
        for col in df.columns:
            if col.startswith('dec'):  # Converter decêntios para numérico
                df[col] = pd.to_numeric(df[col].replace(',', '.', regex=True), errors='coerce')
            elif col == 'safra_ini':  # Ajustar safra_ini para inteiro
                df[col] = pd.to_numeric(df[col], errors='coerce', downcast='integer')
            elif col in ['safra_fin', 'uf', 'municipio', 'nome_cultura', 'nome_clima', 'nome_outros_manejos', 'produtividade', 'portaria']:
                # Converter apenas valores não string para string
                df[col] = df[col].fillna("").astype(str).str.strip().str[:255]

        # Log de quantidade de linhas processadas
        logging.info(f"Linhas a serem carregadas: {len(df)}")

        # Inserir no banco de dados
        logging.info(f"Carregando os dados na tabela {table_name}...")
        with engine.begin() as connection:  # Gerenciar a transação explicitamente
            df.to_sql(table_name, con=connection, if_exists='replace', index=False)
        logging.info(f"Dados carregados com sucesso na tabela {table_name}!")

    except Exception as e:
        logging.error(f"Erro ao processar e carregar o CSV {csv_path} na tabela {table_name}: {e}")

def parse_metadata(file_path):
    """Lê os metadados do início do arquivo."""
    metadata = {}
    try:
        with open(file_path, 'r', encoding='iso-8859-1') as f:
            for _ in range(8):  # Ler as 8 primeiras linhas de metadados
                line = f.readline().strip()
                if ":" in line:
                    key, value = line.split(':;', 1)
                    metadata[key.strip()] = value.strip().replace(',', '.')  # Substituir vírgula por ponto

        # Validar metadados obrigatórios
        missing_keys = [key for key in required_keys if key not in metadata]
        if missing_keys:
            raise ValueError(f"Faltando chaves obrigatórias: {missing_keys}")

    except ValueError as ve:
        logging.error(f"Erro de validação de metadados no arquivo {file_path}: {ve}")
    except Exception as e:
        logging.error(f"Erro ao ler os metadados do arquivo {file_path}: {e}")
    return metadata


# Função para processar valores numéricos
def clean_numeric_column(df, column_name):
    if column_name in df.columns:
        df[column_name] = (
            df[column_name]
            .astype(str)
            .str.replace('.', '', regex=False)  # Remove pontos
            .str.replace(',', '.', regex=False)  # Troca vírgulas por pontos
            .astype(float)  # Converte para float
        )

def clean_numeric_columns(df):
    """Remove caracteres não numéricos e converte valores para float."""
    for col in df.columns:
        if df[col].dtype == 'object':  # Apenas processar colunas do tipo string
            df[col] = df[col].str.replace(',', '.', regex=False)  # Substituir vírgula por ponto
        df[col] = pd.to_numeric(df[col], errors='coerce')  # Converter para numérico
    return df



# Função Principal para Processar Arquivo Individual
def process_climate_file(file_path, engine):
    try:
        # Detectar codificação
        encoding = detect_encoding(file_path)
        logging.info(f"Detectada a codificação do arquivo {file_path}: {encoding}")

        # Ler metadados
        metadata = parse_metadata(file_path)
        if not metadata:
            logging.error(f"Metadados ausentes ou inválidos no arquivo {file_path}.")
            return

        # Inserir metadados na tabela 'stations'
        with engine.begin() as connection:
            station_query = """
                INSERT INTO stations (regiao, uf, estacao, codigo_wmo, latitude, longitude, altitude, data_fundacao)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
            """
            station_id = connection.execute(
                station_query,
                [
                    metadata["REGIAO"],
                    metadata["UF"],
                    metadata["ESTACAO"],
                    metadata["CODIGO (WMO)"],
                    float(metadata["LATITUDE"]),
                    float(metadata["LONGITUDE"]),
                    float(metadata["ALTITUDE"]),
                    datetime.strptime(metadata["DATA DE FUNDACAO"], "%d/%m/%y").strftime("%Y-%m-%d"),
                ]
            ).scalar()

        logging.info(f"Metadados inseridos com station_id {station_id}")

        # Ler dados climáticos
        df = pd.read_csv(file_path, sep=";", encoding=encoding, skiprows=8)

        # Renomear colunas
        df.rename(columns=column_mapping_clima, inplace=True)
        colunas_amostra = df.columns
        logging.info(f"colunas avaliadas {colunas_amostra}")
        # Verificar se a coluna 'data' está presente
        if 'data' not in df.columns:
            logging.error(f"A coluna 'data' está ausente no arquivo {file_path}. Colunas encontradas: {list(df.columns)}")
            return

        # Converter colunas numéricas
        numeric_columns = list(column_mapping_clima.values())[2:]  # Exclui 'data' e 'hora_utc'
        df = clean_numeric_columns(df)

        # Adicionar station_id
        df["station_id"] = station_id

        # Remover registros sem data
        df.dropna(subset=["data"], inplace=True)

        # Carregar dados no banco
        with engine.begin() as connection:
            df.to_sql("climate_data", con=connection, if_exists="append", index=False)

        logging.info(f"Arquivo {file_path} processado com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao processar arquivo {file_path}: {e}")

# Função para detectar codificação
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(10000))  # Detecta com base nos primeiros 10KB
        return result['encoding']

# Função para detectar delimitador
def detect_delimiter(file_path, encoding):
    with open(file_path, 'r', encoding=encoding) as f:
        first_line = f.readline()
        if ',' in first_line:
            return ','
        elif ';' in first_line:
            return ';'
        else:
            return ','  # Padrão

# Função para normalizar cabeçalhos
def normalize_headers(headers):
    return [header.strip().lower().replace(" ", "_").replace(";", "").replace(":", "") for header in headers]



# Função para Processar Vários Arquivos
def process_climate_files(base_path, engine):
    files = [os.path.join(base_path, f) for f in os.listdir(base_path) if f.endswith(".CSV")]
    for file in files:
        try:
            process_climate_file(file, engine)
        except Exception as e:
            logging.error(f"Erro ao processar arquivo {file}: {e}")

# Executar o processamento com o engine como argumento
base_path = "/app/data/clima"
process_climate_files(base_path, engine)
# Processar e carregar o arquivo filtrado
csv_path = "/app/data/df_filtrado.csv"
table_name = "tabua_de_risco"
clean_and_load_filtered_csv(csv_path, table_name, column_mapping)# Processar e carregar o arquivo filtrado

# Tabelas menores
files_to_tables = {
    "/app/data/arroz.csv": ("arroz", ['localidade', 'unidade', 'jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']),
    "/app/data/milho.csv": ("milho", ['localidade', 'unidade', 'jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']),
    "/app/data/soja.csv": ("soja", ['localidade', 'unidade', 'jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']),
    "/app/data/TRIGO.csv": ("trigo", ['localidade', 'unidade', 'jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']),
    "/app/data/sipeagrofertilizante.csv": ("fertilizantes", ['unidade_federacao', 'municipio', 'numero_registro', 'status_registro', 'cnpj', 'razao_social', 'nome_fantasia', 'area_atuacao', 'atividade', 'classificacao']),
    "/app/data/sigefdeclaracaoareaproducao.csv": ("declaracao_producao", ['tipo_periodo', 'periodo', 'area_total', 'municipio', 'uf', 'especie', 'cultivar', 'area_plantada', 'area_estimada', 'quant_reservada', 'data_plantio']),
    "/app/data/sigefcamposproducaodesementes.csv": ("producao_semente", ['safra', 'especie', 'categoria', 'cultivar', 'municipio', 'uf', 'status', 'data_plantio', 'data_colheita', 'area', 'producao_bruta', 'producao_estimada']),
    "/app/data/sementes.csv": ("semente", ['produto', 'unidade', 'uf', 'ano', 'jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']),
    "/app/data/FERTILIZANTES.csv": ("producao_fertilizantes", ['produto', 'unidade', 'uf', 'ano', 'jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']),
    "/app/data/AGROTOXICO.csv": ("agrotoxico", ['produto', 'unidade', 'uf', 'ano', 'jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']),
    "/app/data/agrofitprodutosformulados.csv": ("registro_agrotoxico", ['nr_registro', 'marca_comercial', 'formulacao', 'ingrediente_ativo', 'titular_de_registro', 'classe', 'modo_de_acao', 'cultura', 'praga_nome_cientifico', 'praga_nome_comum', 'empresa_pais_tipo', 'classe_toxicologica', 'classe_ambiental', 'organicos', 'situacao']),
    "/app/data/estados.csv": ("regions", ['COD,NOME,SIGLA,REGIAO']),
    "/app/data/raw_data/rendimento/ranking-agricultura-valor-da-produo-brasil.csv": 
        ("ranking_agricultura_valor", {"produto": "produto", "valor": "valor", "unidade": "unidade"}),
    "/app/data/raw_data/rendimento/arrozsolo_transformado.csv": 
        ("arroz_solo_transformado", {"Safra": "safra", "Cultura": "cultura", "UF": "uf", "Município": "municipio",
                                     "Grupo": "grupo", "Solo": "solo", "Outros manejos": "outros_manejos",
                                     "Clima": "clima", "Decênio": "decenio", "Valor": "valor", "Data": "data"}),
    "/app/data/raw_data/rendimento/milhosolo_transformado.csv": 
        ("milho_solo_transformado", {"Safra": "safra", "Cultura": "cultura", "UF": "uf", "Município": "municipio",
                                     "Grupo": "grupo", "Solo": "solo", "Outros manejos": "outros_manejos",
                                     "Clima": "clima", "Decênio": "decenio", "Valor": "valor", "Data": "data"}),
    "/app/data/raw_data/rendimento/sojasolo_transformado.csv": 
        ("soja_solo_transformado", {"Safra": "safra", "Cultura": "cultura", "UF": "uf", "Município": "municipio",
                                    "Grupo": "grupo", "Solo": "solo", "Outros manejos": "outros_manejos",
                                    "Clima": "clima", "Decênio": "decenio", "Valor": "valor", "Data": "data"}),
    "/app/data/raw_data/rendimento/trigosolo_transformado.csv": 
        ("trigo_solo_transformado", {"Safra": "safra", "Cultura": "cultura", "UF": "uf", "Município": "municipio",
                                     "Grupo": "grupo", "Solo": "solo", "Outros manejos": "outros_manejos",
                                     "Clima": "clima", "Decênio": "decenio", "Valor": "valor", "Data": "data"})
                                     
}

# Processar arquivos menores
for file_path, (table_name, headers) in files_to_tables.items():
    load_csv_to_table(file_path, table_name, headers)