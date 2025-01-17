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

def process_row(row, categorical_fields, numeric_fields):
    """
    Processa uma linha bruta de dados e ajusta ao esquema correto.

    Args:
        row (dict): Linha de dados brutos.
        categorical_fields (list): Lista de campos categóricos esperados.
        numeric_fields (list): Lista de campos numéricos esperados.

    Returns:
        dict: Linha processada com valores ajustados.
    """
    row_out = {}

    # Processar campos categóricos
    for field in categorical_fields:
        row_out[field] = row.get(field, "Desconhecido")  # Valor padrão para campos categóricos ausentes

    # Processar campos numéricos
    for field in numeric_fields:
        try:
            row_out[field] = float(row.get(field, 0))  # Valor padrão 0 se ausente ou inválido
        except (ValueError, TypeError):
            print(f"Erro ao converter o campo '{field}' para float na linha: {row}. Atribuindo valor padrão 0.")
            row_out[field] = 0

    # Adicionar coluna 'split_value'
    try:
        row_out["split_value"] = float(row.get("split", 0))  # Valor padrão 0 se ausente ou inválido
    except (ValueError, TypeError):
        print(f"Erro ao converter o campo 'split' para float na linha: {row}. Atribuindo valor padrão 0.")
        row_out["split_value"] = 0

    return row_out

def validate_rendimento_raw(file_path):
    """
    Valida se o arquivo rendimento_raw.csv contém as colunas esperadas.
    """
    expected_columns = ["safra", "cultura", "uf", "municipio", "grupo", "solo",
                        "outros_manejos", "clima", "decenio", "valor", "data",
                        "Valor da Produção Total", "Área colhida (ha)", "split_value"]
    colunas_tipos = {
        "safra": "string",
        "cultura": "string",
        "uf": "string",
        "municipio": "string",
        "grupo": "string",
        "solo": "string",
        "outros_manejos": "string",
        "clima": "string",
        "decenio": "string",
        "valor": "float64",
        "data": "string",
        "Valor da Produção Total": "float64",
        "Área colhida (ha)": "float64",
        "split_value": "float64",
    }
    try:
        df = pd.read_csv(file_path, dtype=colunas_tipos, low_memory=False)
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            print(f"As colunas seguintes estão faltando: {missing_columns}")
        else:
            print("Todas as colunas esperadas estão presentes no arquivo rendimento_raw.csv.")
    except Exception as e:
        print(f"Erro ao validar rendimento_raw: {e}")
#voltando
def create_rendimento_raw():
    """
    Cria o arquivo `rendimento_raw.csv` combinando dados e processando os datasets em chunks.
    """
    inicio = time.time()
    try:
        log_memory_usage("Antes de carregar tabelas para rendimento_raw")

        # Tamanhos de chunk
        chunksize = 5000  # Ajuste conforme necessário

        # Carregar datasets em chunks
        milho_chunks = pd.read_sql("SELECT * FROM milho_solo_transformado", con=engine, chunksize=chunksize)
        arroz_chunks = pd.read_sql("SELECT * FROM arroz_solo_transformado", con=engine, chunksize=chunksize)
        ranking_valores = pd.read_sql("SELECT * FROM ranking_agricultura_valor", con=engine)

        # Garantir colunas consistentes para ranking_valores
        ranking_valores.rename(columns={"produto": "Cultura", "valor": "Valor da Produção Total"}, inplace=True)
        ranking_valores["Valor da Produção Total"] = ranking_valores["Valor da Produção Total"].str.replace('.', '', regex=False).astype(float)

        log_memory_usage("Antes de combinar dados")

        # Processar milho e arroz em chunks
        output_path = "data/raw_data/rendimento/rendimento_raw.csv"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        for milho_chunk, arroz_chunk in zip(milho_chunks, arroz_chunks):
            milho_chunk["Cultura"] = "Milho"
            arroz_chunk["Cultura"] = "Arroz"

            # Combinar os dados do chunk atual
            dados_combinados = pd.concat([milho_chunk, arroz_chunk], ignore_index=True)
            dados_combinados = dados_combinados.merge(ranking_valores, on="Cultura", how="left").fillna(0)

            # Garantir colunas esperadas
            if "Área colhida (ha)" not in dados_combinados.columns:
                dados_combinados["Área colhida (ha)"] = 0.0  # Valor padrão

            # Salvar o chunk no arquivo de saída
            dados_combinados.to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False)

            log_memory_usage("Depois de processar um chunk")

        log_tempo(inicio, "Arquivo rendimento_raw.csv criado com sucesso")

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