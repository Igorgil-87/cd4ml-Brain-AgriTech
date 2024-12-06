from cd4ml.filenames import get_problem_files
from cd4ml.utils.utils import download_to_file_from_url
import pandas as pd
from sqlalchemy import create_engine
import os

# Configuração do banco de dados
DB_CONFIG = {
    "database": "brain_agro",
    "user": "agro_user",
    "password": "agro_password",
    "host": "postgres",  # Ajuste conforme necessário
    "port": "5432"
}

# Consultas SQL
QUERIES_COMMODITIES = {
    "arroz": "SELECT * FROM arroz;",
    "milho": "SELECT * FROM milho;",
    "soja": "SELECT * FROM soja;",
    "trigo": "SELECT * FROM trigo;"
}

QUERY_REGIONS = """
SELECT * FROM regions;  -- Certifique-se de que esta tabela contém informações sobre regiões
"""

# URLs simuladas para os arquivos locais
LOCAL_FILE_SERVER_BASE_URL = "http://localhost/files"

def save_and_generate_url(dataframe, filename):
    """
    Salva um DataFrame localmente e retorna a URL simulada para o arquivo.
    """
    local_dir = "/tmp/commodities"  # Diretório temporário para os arquivos locais
    os.makedirs(local_dir, exist_ok=True)
    local_path = os.path.join(local_dir, filename)
    dataframe.to_csv(local_path, index=False)
    print(f"Arquivo salvo em: {local_path}")
    return f"{LOCAL_FILE_SERVER_BASE_URL}/{filename}"

def download(use_cache=True):
    """
    Baixa os dados do banco de dados e utiliza `download_to_file_from_url` para simular o download.
    """
    # Conexão com o banco de dados
    engine = create_engine(
        f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )

    # Obtenção dos caminhos de saída
    file_names = get_problem_files("commodities")
    commodities_data_path = file_names["raw_commodities_data"]
    regions_data_path = file_names["commodities_regions_lookup"]

    # Baixar e combinar dados de commodities
    all_commodities = []
    for commodity, query in QUERIES_COMMODITIES.items():
        print(f"Baixando dados para {commodity}...")
        df = pd.read_sql_query(query, con=engine)
        df['commodity'] = commodity  # Adiciona uma coluna para identificar a commodity
        all_commodities.append(df)

    combined_commodities_df = pd.concat(all_commodities, ignore_index=True)
    url_combined = save_and_generate_url(combined_commodities_df, "combined_commodities.csv")

    # Simulando o download do arquivo combinado
    print(f"Baixando dados combinados de commodities de {url_combined}...")
    download_to_file_from_url(url_combined, commodities_data_path, use_cache)

    # Baixar dados de regiões
    regions_df = pd.read_sql_query(QUERY_REGIONS, con=engine)
    url_regions = save_and_generate_url(regions_df, "regions.csv")

    # Simulando o download dos dados de regiões
    print(f"Baixando dados de regiões de {url_regions}...")
    download_to_file_from_url(url_regions, regions_data_path, use_cache)

if __name__ == "__main__":
    download()