import shutil
from cd4ml.filenames import get_problem_files
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração do banco de dados usando .env
DB_CONFIG = {
    "database": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": "postgres",  # Substitua pelo serviço/host correto
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

def test_db_connection(engine):
    """ Testa a conexão ao banco de dados. """
    try:
        with engine.connect() as connection:
            print("Conexão ao banco de dados bem-sucedida!")
    except Exception as e:
        print("Erro ao conectar ao banco de dados:", e)
        exit(1)

def save_dataframe(dataframe, filename):
    """ Salva um DataFrame localmente no diretório configurado. """
    local_dir = "/tmp/commodities"  # Diretório temporário para os arquivos locais
    os.makedirs(local_dir, exist_ok=True)
    local_path = os.path.join(local_dir, filename)
    dataframe.to_csv(local_path, index=False)
    print(f"Arquivo salvo em: {local_path}")
    return local_path

def move_file(source, destination):
    """ Move um arquivo entre sistemas de arquivos diferentes. """
    shutil.copy2(source, destination)
    os.remove(source)
    print(f"Arquivo movido de {source} para {destination}")

def download(use_cache=True):
    """
    Baixa os dados do banco de dados e os salva diretamente no local configurado.
    """
    # Conexão com o banco de dados
    engine = create_engine(
        f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )

    # Testa a conexão com o banco
    test_db_connection(engine)

    # Obtenção dos caminhos de saída
    file_names = get_problem_files("commodities")
    commodities_data_path = file_names["raw_commodities_data"]
    regions_data_path = file_names["commodities_regions_lookup"]

    # Baixar e combinar dados de commodities
    all_commodities = []
    for commodity, query in QUERIES_COMMODITIES.items():
        print(f"Executando query para {commodity}: {query}")
        try:
            df = pd.read_sql_query(query, con=engine)
            print(f"Linhas retornadas para {commodity}: {len(df)}")
            if not df.empty:
                df['commodity'] = commodity  # Adiciona uma coluna para identificar a commodity
                all_commodities.append(df)
            else:
                print(f"Aviso: Nenhum dado encontrado para {commodity}.")
        except Exception as e:
            print(f"Erro ao executar query para {commodity}: {e}")

    if all_commodities:
        combined_commodities_df = pd.concat(all_commodities, ignore_index=True)
        combined_file_path = save_dataframe(combined_commodities_df, "combined_commodities.csv")

        # Salvar os dados combinados no caminho esperado
        print(f"Copiando dados combinados para {commodities_data_path}...")
        move_file(combined_file_path, commodities_data_path)
    else:
        print("Erro: Nenhum dado válido encontrado para commodities.")
        return

    # Baixar dados de regiões
    print("Executando query para regiões...")
    try:
        regions_df = pd.read_sql_query(QUERY_REGIONS, con=engine)
        print(f"Linhas retornadas para regiões: {len(regions_df)}")
        if not regions_df.empty:
            regions_file_path = save_dataframe(regions_df, "regions.csv")

            # Salvar os dados de regiões no caminho esperado
            print(f"Copiando dados de regiões para {regions_data_path}...")
            move_file(regions_file_path, regions_data_path)
        else:
            print("Erro: Nenhum dado encontrado para a tabela 'regions'.")
    except Exception as e:
        print(f"Erro ao executar query para regiões: {e}")

if __name__ == "__main__":
    download()