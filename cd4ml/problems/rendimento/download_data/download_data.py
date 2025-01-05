from sqlalchemy import create_engine
import pandas as pd
import time

# Função para log do tempo
def log_tempo(inicio, mensagem):
    print(f"{mensagem} - Tempo decorrido: {time.time() - inicio:.2f} segundos")

# Configuração do banco de dados
DB_CONFIG = {
    "database": "brain_agro",
    "user": "agro_user",
    "password": "agro_password",
    "host": "postgres",  # Ajuste se necessário
    "port": "5432"
}

# Criação da string de conexão SQLAlchemy
connection_string = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(connection_string)

# Função para realizar a consulta no banco e buscar os dados
def query_db(table_name, chunksize=None):
    inicio = time.time()
    query = f"SELECT * FROM {table_name}"
    try:
        if chunksize:
            chunks = []
            for chunk in pd.read_sql(query, engine, chunksize=chunksize):
                chunks.append(chunk)
            df = pd.concat(chunks, ignore_index=True)
        else:
            df = pd.read_sql(query, engine)
        log_tempo(inicio, f"Dados carregados da tabela {table_name}")
        return df
    except Exception as e:
        print(f"Erro ao carregar tabela {table_name}: {e}")
        return None

# Função para limpar e converter valores
def clean_and_convert(df, column_name):
    """
    Remove separadores de milhares e converte a coluna para float.
    """
    try:
        df[column_name] = (
            df[column_name]
            .str.replace('.', '', regex=False)  # Remove separadores de milhares
            .str.replace(',', '.', regex=False)  # Substitui vírgulas por pontos
            .astype(float)
        )
    except Exception as e:
        print(f"Erro ao limpar e converter a coluna {column_name}: {e}")
# Função para criar o arquivo rendimento_raw
def create_rendimento_raw():
    inicio = time.time()
    try:
        # Consultar tabelas do banco de dados
        milho = pd.read_sql("SELECT * FROM milho_solo_transformado", con=engine)
        arroz = pd.read_sql("SELECT * FROM arroz_solo_transformado", con=engine)
        ranking_valores = pd.read_sql("SELECT * FROM ranking_agricultura_valor", con=engine)
        
        # Processar tabela ranking de valores
        ranking_valores.rename(columns={"produto": "Cultura", "valor": "Valor da Produção Total"}, inplace=True)
        ranking_valores['Valor da Produção Total'] = ranking_valores['Valor da Produção Total'].str.replace('.', '').astype(float)
        
        # Merge e preenchimento
        dados_combinados = pd.concat([milho, arroz], ignore_index=True)
        dados_combinados = dados_combinados.merge(ranking_valores, on="Cultura", how="left").fillna(0)

        # Salvar como rendimento_raw.csv
        output_path = "data/raw_data/rendimento/rendimento_raw.csv"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        dados_combinados.to_csv(output_path, index=False)
        log_tempo(inicio, "Arquivo rendimento_raw.csv criado com sucesso")
    except Exception as e:
        print(f"Erro ao criar rendimento_raw: {e}")



# Função principal de download
def download(problem_name=None):
    """
    Função para carregar e processar os dados diretamente do banco de dados.
    """
    print(f"Executando download para o problema: {problem_name}" if problem_name else "Executando download...")

    # Carregar dados de ranking de valores
    ranking_valores = query_db("ranking_agricultura_valor", chunksize=1000)
    if ranking_valores is not None:
        ranking_valores.rename(columns={"produto": "Cultura", "valor": "Valor da Produção Total"}, inplace=True)
        clean_and_convert(ranking_valores, "Valor da Produção Total")

    # Carregar dados do IBGE (dados fixos no código)
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

    # Carregar dados combinados (milho, soja, trigo, arroz)
    milho_transformado = query_db("milho_solo_transformado", chunksize=1000)
    #soja_transformado = query_db("soja_solo_transformado", chunksize=1000)
    #trigo_transformado = query_db("trigo_solo_transformado", chunksize=1000)
    arroz_transformado = query_db("arroz_solo_transformado", chunksize=1000)

    # Combinar todos os dados
    inicio = time.time()
    dados_combinados = pd.concat([
        milho_transformado,
        #soja_transformado,
        #trigo_transformado,
        arroz_transformado
    ], ignore_index=True)
    log_tempo(inicio, "Dados transformados combinados")

    # Chamar a função de criação de rendimento_raw
    print("Criando o arquivo rendimento_raw.csv...")
    rendimento_raw_df = create_rendimento_raw()

    print("Download completo.")
    # Retornar todos os datasets carregados
    return ranking_valores, dados_ibge_df, dados_combinados, rendimento_raw_df