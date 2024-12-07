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

def save_dataframe(dataframe, filename):
    """
    Salva um DataFrame localmente no diretório configurado.
    """
    local_dir = "/tmp/commodities"  # Diretório temporário para os arquivos locais
    os.makedirs(local_dir, exist_ok=True)
    local_path = os.path.join(local_dir, filename)
    dataframe.to_csv(local_path, index=False)
    print(f"Arquivo salvo em: {local_path}")
    return local_path

def download(use_cache=True):
    """
    Baixa os dados do banco de dados e os salva diretamente no local configurado.
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
        if not df.empty:
            df['commodity'] = commodity  # Adiciona uma coluna para identificar a commodity
            all_commodities.append(df)
        else:
            print(f"Aviso: Nenhum dado encontrado para {commodity}.")

    if all_commodities:
        combined_commodities_df = pd.concat(all_commodities, ignore_index=True)
        combined_file_path = save_dataframe(combined_commodities_df, "combined_commodities.csv")

        # Salvar os dados combinados no caminho esperado
        print(f"Copiando dados combinados para {commodities_data_path}...")
        os.replace(combined_file_path, commodities_data_path)
    else:
        print("Erro: Nenhum dado válido encontrado para commodities.")
        return

    # Baixar dados de regiões
    print("Baixando dados de regiões...")
    regions_df = pd.read_sql_query(QUERY_REGIONS, con=engine)
    if not regions_df.empty:
        regions_file_path = save_dataframe(regions_df, "regions.csv")

        # Salvar os dados de regiões no caminho esperado
        print(f"Copiando dados de regiões para {regions_data_path}...")
        os.replace(regions_file_path, regions_data_path)
    else:
        print("Erro: Nenhum dado encontrado para a tabela 'regions'.")

if __name__ == "__main__":
    download()