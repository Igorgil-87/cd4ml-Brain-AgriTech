import os
import time
import pandas as pd
from sqlalchemy import create_engine
import psutil

# Funções auxiliares para log
def log_tempo(inicio, mensagem):
    print(f"{mensagem} - Tempo decorrido: {time.time() - inicio:.2f} segundos")

def log_memory_usage(stage):
    process = psutil.Process()
    print(f"Memory usage at {stage}: {process.memory_info().rss / (1024 * 1024):.2f} MB")

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

# Função para consultar tabelas com validação
def query_db_safe(table_name, chunksize=1000):
    try:
        data = pd.read_sql(f"SELECT * FROM {table_name}", con=engine, chunksize=chunksize)
        print(f"Tabela {table_name} carregada com sucesso.")
        return data
    except Exception as e:
        print(f"Erro ao carregar a tabela {table_name}: {e}")
        return None

# Função para criar rendimento_raw
def create_rendimento_raw():
    inicio = time.time()
    try:
        log_memory_usage("Antes de carregar tabelas para rendimento_raw")

        # Consultar tabelas
        milho = query_db_safe("milho_solo_transformado")
        arroz = query_db_safe("arroz_solo_transformado")
        ranking_valores = query_db_safe("ranking_agricultura_valor")

        if milho is None or arroz is None or ranking_valores is None:
            print("Erro: Uma ou mais tabelas não foram carregadas. Abortando criação do rendimento_raw.")
            return

        # Processar ranking_valores
        ranking_valores.rename(columns={"produto": "Cultura", "valor": "Valor da Produção Total"}, inplace=True)
        ranking_valores['Valor da Produção Total'] = ranking_valores['Valor da Produção Total'].str.replace('.', '').astype(float)

        log_memory_usage("Antes de combinar dados")
        dados_combinados = pd.concat([milho, arroz], ignore_index=True)
        dados_combinados = dados_combinados.merge(ranking_valores, on="Cultura", how="left").fillna(0)

        log_memory_usage("Antes de salvar rendimento_raw")
        output_path = "data/raw_data/rendimento/rendimento_raw.csv"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        dados_combinados.to_csv(output_path, index=False)
        log_tempo(inicio, "Arquivo rendimento_raw.csv criado com sucesso")
        log_memory_usage("Depois de salvar rendimento_raw")
    except Exception as e:
        print(f"Erro ao criar rendimento_raw: {e}")

# Função principal de download
def download(problem_name=None):
    """
    Função para carregar e processar os dados diretamente do banco de dados.
    """
    print(f"Executando download para o problema: {problem_name}" if problem_name else "Executando download...")
    log_memory_usage("Início do download")

    # Carregar dados de ranking de valores
    ranking_valores = query_db_safe("ranking_agricultura_valor")
    if ranking_valores is None:
        print("Erro: ranking_agricultura_valor não foi carregada. Abortando download.")
        return

    ranking_valores.rename(columns={"produto": "Cultura", "valor": "Valor da Produção Total"}, inplace=True)
    ranking_valores['Valor da Produção Total'] = ranking_valores['Valor da Produção Total'].str.replace('.', '').astype(float)

    # Carregar dados fixos do IBGE
    inicio = time.time()
    dados_ibge = {
        "Milho": {"Área colhida (ha)": 13767431, "Rendimento médio (kg/ha)": 3785, "Quantidade produzida (t)": 52112217},
        "Soja": {"Área colhida (ha)": 20565279, "Rendimento médio (kg/ha)": 2813, "Quantidade produzida (t)": 57857172},
        "Trigo": {"Área colhida (ha)": 1853224, "Rendimento médio (kg/ha)": 2219, "Quantidade produzida (t)": 4114057},
        "Arroz": {"Área colhida (ha)": 2890926, "Rendimento médio (kg/ha)": 3826, "Quantidade produzida (t)": 11060741},
    }
    dados_ibge_df = pd.DataFrame.from_dict(dados_ibge, orient='index').reset_index()
    dados_ibge_df.rename(columns={'index': 'Cultura'}, inplace=True)
    log_tempo(inicio, "Dados do IBGE carregados")
    log_memory_usage("Depois de carregar dados do IBGE")

    # Carregar dados de milho e arroz
    milho_transformado = query_db_safe("milho_solo_transformado")
    arroz_transformado = query_db_safe("arroz_solo_transformado")

    if milho_transformado is None or arroz_transformado is None:
        print("Erro: milho_solo_transformado ou arroz_solo_transformado não foram carregadas. Abortando download.")
        return

    log_memory_usage("Antes de combinar dados transformados")
    dados_combinados = pd.concat([milho_transformado, arroz_transformado], ignore_index=True)
    log_tempo(inicio, "Dados transformados combinados")
    log_memory_usage("Depois de combinar dados transformados")

    # Criar rendimento_raw
    create_rendimento_raw()
    log_memory_usage("Depois de criar rendimento_raw")

    print("Download completo.")
    return ranking_valores, dados_ibge_df, dados_combinados