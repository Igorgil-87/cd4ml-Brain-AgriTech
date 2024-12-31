import logging
from datetime import datetime
import os
from datetime import datetime

def parse_date(date_str):
    """
    Tenta converter uma string de data em formato válido.
    Aceita '%d/%m/%Y' ou '%d/%m/%y'.
    """
    for fmt in ('%d/%m/%Y', '%d/%m/%y'):
        try:
            return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    raise ValueError(f"Formato de data inválido: {date_str}")


def process_stations(file_path, engine):
    """
    Processa o arquivo de metadados das estações e insere os dados na tabela 'stations'.
    """
    try:
        # Garantir que a tabela 'stations' existe
        ensure_table_exists(engine)

        # Ler os metadados do arquivo
        metadata = parse_metadata(file_path)
        if not metadata:
            logging.error(f"Metadados ausentes ou inválidos no arquivo {file_path}.")
            return

        # Substituir vírgulas por pontos nos valores de latitude, longitude e altitude
        metadata["LATITUDE"] = float(metadata["LATITUDE"].replace(",", "."))
        metadata["LONGITUDE"] = float(metadata["LONGITUDE"].replace(",", "."))
        metadata["ALTITUDE"] = float(metadata["ALTITUDE"].replace(",", "."))

        # Converter a data de fundação
        metadata["DATA DE FUNDACAO"] = parse_date(metadata["DATA DE FUNDACAO"])

        # Inserir os metadados no banco de dados
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
                    metadata["LATITUDE"],
                    metadata["LONGITUDE"],
                    metadata["ALTITUDE"],
                    metadata["DATA DE FUNDACAO"],
                ]
            ).scalar()

        logging.info(f"Metadados inseridos com station_id {station_id}")
        return station_id

    except Exception as e:
        logging.error(f"Erro ao processar metadados de 'stations': {e}")
        raise

def load_stations(engine, base_path="/app/data/clima"):
    """
    Processa múltiplos arquivos de metadados e insere as informações na tabela 'stations'.
    """
    files = [os.path.join(base_path, f) for f in os.listdir(base_path) if f.endswith(".CSV")]
    for file in files:
        try:
            process_stations(file, engine)
        except Exception as e:
            logging.error(f"Erro ao processar arquivo {file}: {e}")


def parse_metadata(file_path):
    """
    Lê e valida os metadados do início do arquivo.
    """
    metadata = {}
    try:
        with open(file_path, 'r', encoding='iso-8859-1') as f:
            for _ in range(8):  # Ler as 8 primeiras linhas de metadados
                line = f.readline().strip()
                if ":" in line:
                    key, value = line.split(':;', 1)
                    metadata[key.strip()] = value.strip()

        # Validar os campos obrigatórios
        required_keys = ["REGIAO", "UF", "ESTACAO", "CODIGO (WMO)", "LATITUDE", "LONGITUDE", "ALTITUDE", "DATA DE FUNDACAO"]
        missing_keys = [key for key in required_keys if key not in metadata]
        if missing_keys:
            raise ValueError(f"Metadados ausentes: {missing_keys}")

        return metadata

    except Exception as e:
        logging.error(f"Erro ao ler os metadados do arquivo {file_path}: {e}")
        return None

def ensure_table_exists(engine):
    """
    Garante que a tabela 'stations' exista no banco de dados. Caso contrário, cria a tabela.
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS stations (
        id SERIAL PRIMARY KEY,
        regiao TEXT NOT NULL,
        uf TEXT NOT NULL,
        estacao TEXT NOT NULL,
        codigo_wmo TEXT,
        latitude DOUBLE PRECISION,
        longitude DOUBLE PRECISION,
        altitude DOUBLE PRECISION,
        data_fundacao DATE
    );
    """
    try:
        with engine.connect() as connection:
            connection.execute(create_table_sql)
        logging.info("Tabela 'stations' verificada/criada com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao verificar/criar a tabela 'stations': {e}")
        raise