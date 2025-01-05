import pandas as pd
import os
import time
import psutil
import gc
from sqlalchemy import create_engine

# Configuração do banco de dados
DB_CONFIG = {
    "database": "brain_agro",
    "user": "agro_user",
    "password": "agro_password",
    "host": "postgres",
    "port": "5432"
}

connection_string = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(connection_string)

# Funções de Log
def log_tempo(inicio, mensagem):
    print(f"{mensagem} - Tempo decorrido: {time.time() - inicio:.2f} segundos")

def log_memory_usage(stage):
    process = psutil.Process()
    memory = process.memory_info().rss / (1024 * 1024)
    print(f"Memory usage at {stage}: {memory:.2f} MB")

def query_db_in_chunks(table_name, chunksize=1000):
    """Consulta dados em chunks para evitar alto uso de memória."""
    try:
        temp_file = f"temp_{table_name}.csv"
        with open(temp_file, "w") as f:
            for i, chunk in enumerate(pd.read_sql(f"SELECT * FROM {table_name}", con=engine, chunksize=chunksize)):
                chunk.to_csv(f, mode="a", header=(i == 0), index=False)
        return temp_file
    except Exception as e:
        print(f"Erro ao carregar tabela {table_name}: {e}")
        return None

def create_rendimento_raw():
    inicio = time.time()
    try:
        log_memory_usage("Antes de carregar tabelas para rendimento_raw")
        
        # Carregar tabelas
        milho = pd.read_sql("SELECT * FROM milho_solo_transformado", con=engine)
        milho["Cultura"] = "Milho"  # Adiciona a coluna Cultura para identificação

        arroz = pd.read_sql("SELECT * FROM arroz_solo_transformado", con=engine)
        arroz["Cultura"] = "Arroz"  # Adiciona a coluna Cultura para identificação

        # Adicionar mais fontes se necessário (ex.: soja, trigo)

        ranking_valores = pd.read_sql("SELECT * FROM ranking_agricultura_valor", con=engine)

        # Log das colunas disponíveis
        print(f"Colunas em milho: {milho.columns}")
        print(f"Colunas em arroz: {arroz.columns}")
        print(f"Colunas em ranking_valores: {ranking_valores.columns}")

        # Processar tabela ranking de valores
        ranking_valores.rename(columns={"produto": "Cultura", "valor": "Valor da Produção Total"}, inplace=True)
        ranking_valores["Valor da Produção Total"] = ranking_valores["Valor da Produção Total"].str.replace('.', '').astype(float)

        log_memory_usage("Antes de combinar dados")
        
        # Combinar dados
        dados_combinados = pd.concat([milho, arroz], ignore_index=True)
        dados_combinados = dados_combinados.merge(ranking_valores, on="Cultura", how="left").fillna(0)

        log_memory_usage("Antes de salvar rendimento_raw")
        
        # Salvar como rendimento_raw.csv
        output_path = "data/raw_data/rendimento/rendimento_raw.csv"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        dados_combinados.to_csv(output_path, index=False)
        log_tempo(inicio, "Arquivo rendimento_raw.csv criado com sucesso")
        log_memory_usage("Depois de salvar rendimento_raw")
    except Exception as e:
        print(f"Erro ao criar rendimento_raw: {e}")


def download(problem_name=None):
    """
    Função para carregar e processar os dados diretamente do banco de dados.
    """
    print(f"Executando download para o problema: {problem_name}" if problem_name else "Executando download...")
    log_memory_usage("Início do download")

    try:
        # Carregar dados do IBGE
        inicio = time.time()
        dados_ibge = {
            "Milho": {"Área colhida (ha)": 13767431, "Rendimento médio (kg/ha)": 3785, "Quantidade produzida (t)": 52112217},
            "Soja": {"Área colhida (ha)": 20565279, "Rendimento médio (kg/ha)": 2813, "Quantidade produzida (t)": 57857172},
            "Trigo": {"Área colhida (ha)": 1853224, "Rendimento médio (kg/ha)": 2219, "Quantidade produzida (t)": 4114057},
            "Arroz": {"Área colhida (ha)": 2890926, "Rendimento médio (kg/ha)": 3826, "Quantidade produzida (t)": 11060741},
        }
        dados_ibge_df = pd.DataFrame.from_dict(dados_ibge, orient="index").reset_index()
        dados_ibge_df.rename(columns={"index": "Cultura"}, inplace=True)
        log_tempo(inicio, "Dados do IBGE carregados")
        log_memory_usage("Depois de carregar dados do IBGE")

        # Criar rendimento_raw
        create_rendimento_raw()
        log_memory_usage("Depois de criar rendimento_raw")
    except Exception as e:
        print(f"Erro durante o download: {e}")

    print("Download completo.")
    print(f"Executando download para o problema: {problem_name}" if problem_name else "Executando download...")
    log_memory_usage("Início do download")

    # Carregar dados de ranking de valores em chunks
    query_db_in_chunks("ranking_agricultura_valor")

    # Dados do IBGE (fixos)
    inicio = time.time()
    dados_ibge = {
        "Milho": {"Área colhida (ha)": 13767431, "Rendimento médio (kg/ha)": 3785, "Quantidade produzida (t)": 52112217},
        "Soja": {"Área colhida (ha)": 20565279, "Rendimento médio (kg/ha)": 2813, "Quantidade produzida (t)": 57857172},
        "Trigo": {"Área colhida (ha)": 1853224, "Rendimento médio (kg/ha)": 2219, "Quantidade produzida (t)": 4114057},
        "Arroz": {"Área colhida (ha)": 2890926, "Rendimento médio (kg/ha)": 3826, "Quantidade produzida (t)": 11060741},
    }
    dados_ibge_df = pd.DataFrame.from_dict(dados_ibge, orient="index").reset_index()
    dados_ibge_df.rename(columns={"index": "Cultura"}, inplace=True)
    log_tempo(inicio, "Dados do IBGE carregados")
    log_memory_usage("Depois de carregar dados do IBGE")

    # Criar rendimento_raw
    create_rendimento_raw()

    print("Download completo.")