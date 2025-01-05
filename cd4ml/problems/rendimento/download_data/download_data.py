from sqlalchemy import create_engine
import pandas as pd
import time
import psutil
import gc

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

def log_tempo(inicio, mensagem):
    print(f"{mensagem} - Tempo decorrido: {time.time() - inicio:.2f} segundos")

def log_memory_usage(stage):
    process = psutil.Process()
    memory = process.memory_info().rss / (1024 * 1024)
    print(f"Memory usage at {stage}: {memory:.2f} MB")

def query_db_in_chunks(table_name, chunksize=1000):
    try:
        chunks = []
        for chunk in pd.read_sql(f"SELECT * FROM {table_name}", con=engine, chunksize=chunksize):
            chunks.append(chunk)
        return pd.concat(chunks, ignore_index=True)
    except Exception as e:
        print(f"Erro ao carregar tabela {table_name}: {e}")
        return None

def create_rendimento_raw():
    inicio = time.time()
    try:
        log_memory_usage("Antes de carregar tabelas para rendimento_raw")
        
        # Processar tabelas em chunks
        milho = query_db_in_chunks("milho_solo_transformado", chunksize=1000)
        arroz = query_db_in_chunks("arroz_solo_transformado", chunksize=1000)
        ranking_valores = query_db_in_chunks("ranking_agricultura_valor", chunksize=1000)
        
        # Corrigir valores e renomear colunas
        ranking_valores.rename(columns={"produto": "Cultura", "valor": "Valor da Produção Total"}, inplace=True)
        ranking_valores["Valor da Produção Total"] = ranking_valores["Valor da Produção Total"].str.replace('.', '', regex=False).astype(float)
        
        log_memory_usage("Antes de combinar dados")
        dados_combinados = pd.concat([milho, arroz], ignore_index=True)
        dados_combinados = dados_combinados.merge(ranking_valores, on="Cultura", how="left").fillna(0)
        
        log_memory_usage("Antes de salvar rendimento_raw")
        output_path = "data/raw_data/rendimento/rendimento_raw.csv"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        dados_combinados.to_csv(output_path, index=False)
        log_tempo(inicio, "Arquivo rendimento_raw.csv criado com sucesso")
        
        del milho, arroz, ranking_valores, dados_combinados  # Liberar memória
        gc.collect()
    except Exception as e:
        print(f"Erro ao criar rendimento_raw: {e}")

def download(problem_name=None):
    print(f"Executando download para o problema: {problem_name}" if problem_name else "Executando download...")
    log_memory_usage("Início do download")

    # Carregar dados de ranking de valores
    ranking_valores = query_db_in_chunks("ranking_agricultura_valor", chunksize=1000)
    if ranking_valores is not None:
        ranking_valores.rename(columns={"produto": "Cultura", "valor": "Valor da Produção Total"}, inplace=True)
        ranking_valores["Valor da Produção Total"] = ranking_valores["Valor da Produção Total"].str.replace('.', '', regex=False).astype(float)

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

    milho_transformado = query_db_in_chunks("milho_solo_transformado", chunksize=1000)
    arroz_transformado = query_db_in_chunks("arroz_solo_transformado", chunksize=1000)

    inicio = time.time()
    dados_combinados = pd.concat([milho_transformado, arroz_transformado], ignore_index=True)
    log_tempo(inicio, "Dados transformados combinados")
    log_memory_usage("Depois de combinar dados transformados")

    create_rendimento_raw()
    log_memory_usage("Depois de criar rendimento_raw")
    
    del milho_transformado, arroz_transformado, ranking_valores, dados_combinados, dados_ibge_df  # Liberar memória
    gc.collect()

    print("Download completo.")