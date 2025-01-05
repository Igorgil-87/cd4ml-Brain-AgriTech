from sqlalchemy import create_engine
import pandas as pd
import os
import time
import psutil

# Função para log de uso de memória
def log_memory_usage(stage):
    process = psutil.Process()
    memory_mb = process.memory_info().rss / (1024 * 1024)
    print(f"Memory usage at {stage}: {memory_mb:.2f} MB")

# Função para log de tempo
def log_tempo(inicio, mensagem):
    elapsed_time = time.time() - inicio
    print(f"{mensagem} - Tempo decorrido: {elapsed_time:.2f} segundos")

# Configuração do banco de dados
DB_CONFIG = {
    "database": "brain_agro",
    "user": "agro_user",
    "password": "agro_password",
    "host": "postgres",  # Ajuste conforme necessário
    "port": "5432"
}

# Criação da string de conexão SQLAlchemy
connection_string = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(connection_string)

# Função para carregar dados do banco com chunks
def query_db_safe(table_name, chunksize=1000):
    try:
        # Usar o gerador para processar os dados em partes
        data_gen = pd.read_sql(f"SELECT * FROM {table_name}", con=engine, chunksize=chunksize)
        for chunk in data_gen:
            yield chunk
    except Exception as e:
        print(f"Erro ao carregar a tabela {table_name}: {e}")
        yield None

# Função para criar o arquivo rendimento_raw
def create_rendimento_raw():
    inicio = time.time()
    try:
        log_memory_usage("Antes de carregar tabelas para rendimento_raw")
        # Carregar dados em chunks para reduzir o consumo de memória
        milho_chunks = query_db_safe("milho_solo_transformado", chunksize=1000)
        arroz_chunks = query_db_safe("arroz_solo_transformado", chunksize=1000)
        ranking_valores_chunks = query_db_safe("ranking_agricultura_valor", chunksize=1000)

        # Concatenar os dados carregados em partes
        milho = pd.concat(milho_chunks, ignore_index=True)
        arroz = pd.concat(arroz_chunks, ignore_index=True)
        ranking_valores = pd.concat(ranking_valores_chunks, ignore_index=True)

        # Processar tabela ranking de valores
        ranking_valores.rename(columns={"produto": "Cultura", "valor": "Valor da Produção Total"}, inplace=True)
        ranking_valores["Valor da Produção Total"] = ranking_valores["Valor da Produção Total"].str.replace('.', '').astype(float)

        log_memory_usage("Antes de combinar dados")
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

# Função principal de download
def download(problem_name=None):
    """
    Função para carregar e processar os dados diretamente do banco de dados.
    """
    inicio = time.time()
    print(f"Executando download para o problema: {problem_name}" if problem_name else "Executando download...")
    log_memory_usage("Início do download")

    try:
        # Carregar dados de ranking de valores
        ranking_valores_chunks = query_db_safe("ranking_agricultura_valor", chunksize=1000)
        ranking_valores = pd.concat(ranking_valores_chunks, ignore_index=True)
        ranking_valores.rename(columns={"produto": "Cultura", "valor": "Valor da Produção Total"}, inplace=True)
        ranking_valores["Valor da Produção Total"] = ranking_valores["Valor da Produção Total"].str.replace('.', '').astype(float)

        log_memory_usage("Depois de carregar ranking_agricultura_valor")

        # Carregar dados do IBGE
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

        # Carregar dados transformados
        milho_chunks = query_db_safe("milho_solo_transformado", chunksize=1000)
        arroz_chunks = query_db_safe("arroz_solo_transformado", chunksize=1000)

        milho_transformado = pd.concat(milho_chunks, ignore_index=True)
        arroz_transformado = pd.concat(arroz_chunks, ignore_index=True)

        dados_combinados = pd.concat([milho_transformado, arroz_transformado], ignore_index=True)
        log_tempo(inicio, "Dados transformados combinados")
        log_memory_usage("Depois de combinar dados transformados")

        # Criar rendimento_raw
        create_rendimento_raw()
        log_memory_usage("Depois de criar rendimento_raw")

        print("Download completo.")
        return ranking_valores, dados_ibge_df, dados_combinados
    except Exception as e:
        print(f"Erro no processo de download: {e}")