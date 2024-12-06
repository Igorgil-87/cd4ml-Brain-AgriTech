import pandas as pd
from sqlalchemy import create_engine
import psycopg2
import csv
import logging

# Configuração do banco de dados
DB_CONFIG = {
    "database": "brain_agro",
    "user": "agro_user",
    "password": "agro_password",
    "host": "postgres",  # Ajuste o host para "localhost" ou outro, conforme necessário
    "port": "5432"
}

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Criação da string de conexão SQLAlchemy
connection_string = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(connection_string)

# Mapeamento completo das colunas
column_mapping = {
    "Nome_cultura": "nome_cultura",
    "SafraIni": "safra_ini",
    "SafraFin": "safra_fin",
    "Cod_Cultura": "cod_cultura",
    "Cod_Ciclo": "cod_ciclo",
    "Cod_Solo": "cod_solo",
    "geocodigo": "geocodigo",
    "UF": "uf",
    "municipio": "municipio",
    "Cod_Clima": "cod_clima",
    "Nome_Clima": "nome_clima",
    "Cod_Outros_Manejos": "cod_outros_manejos",
    "Nome_Outros_Manejos": "nome_outros_manejos",
    "Produtividade": "produtividade",
    "Cod_Munic": "cod_munic",
    "Cod_Meso": "cod_meso",
    "Cod_Micro": "cod_micro",
    "Portaria": "portaria",
    **{f"dec{i}": f"dec{i}" for i in range(1, 37)}  # Adicionar todos os decêntios
}

def clean_and_load_filtered_csv(csv_path, table_name, column_mapping):
    try:
        logging.info(f"Lendo o arquivo CSV filtrado: {csv_path}")
        df = pd.read_csv(csv_path, sep=';', low_memory=False)

        # Renomear colunas para corresponder à tabela do banco de dados
        df.rename(columns=column_mapping, inplace=True)

        # Tratamento de dados
        for col in df.columns:
            if col.startswith('dec'):  # Converter decêntios para numérico
                df[col] = pd.to_numeric(df[col].replace(',', '.', regex=True), errors='coerce')
            elif col == 'safra_ini':  # Ajustar safra_ini para inteiro
                df[col] = pd.to_numeric(df[col], errors='coerce', downcast='integer')
            elif col in ['safra_fin', 'uf', 'municipio', 'nome_cultura', 'nome_clima', 'nome_outros_manejos', 'produtividade', 'portaria']:
                # Converter apenas valores não string para string
                df[col] = df[col].fillna("").astype(str).str.strip().str[:255]

        # Log de quantidade de linhas processadas
        logging.info(f"Linhas a serem carregadas: {len(df)}")

        # Inserir no banco de dados
        logging.info(f"Carregando os dados na tabela {table_name}...")
        with engine.begin() as connection:  # Gerenciar a transação explicitamente
            df.to_sql(table_name, con=connection, if_exists='replace', index=False)
        logging.info(f"Dados carregados com sucesso na tabela {table_name}!")

    except Exception as e:
        logging.error(f"Erro ao processar e carregar o CSV {csv_path} na tabela {table_name}: {e}")


def clean_csv_data(csv_path, headers=None):
    """Limpa e normaliza os dados do CSV."""
    df = pd.read_csv(csv_path, sep=';', low_memory=False, on_bad_lines='skip', encoding='utf-8')

    # Remover colunas extras, como 'Unnamed:'
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    # Corrigir espaços extras nos nomes das colunas
    df.columns = df.columns.str.strip()

    if headers:
        # Verificar se o número de colunas corresponde
        if len(headers) != len(df.columns):
            logging.error(f"Desajuste de colunas no arquivo {csv_path}. "
                          f"Esperado: {len(headers)}, Encontrado: {len(df.columns)}")
            logging.error(f"Colunas encontradas: {list(df.columns)}")
            raise ValueError("Desajuste no número de colunas.")
        df.columns = headers

    # Substituir vírgulas por pontos em colunas numéricas
    for col in df.columns:
        if df[col].dtype == 'object':  # Apenas processar colunas de texto
            df[col] = df[col].str.replace(',', '.', regex=False)  # Substituir vírgula por ponto
        if col not in ['localidade', 'unidade', 'uf', 'municipio']:  # Ignorar colunas não numéricas
            df[col] = pd.to_numeric(df[col], errors='coerce')  # Converter para numérico, ignorando erros

    return df

def load_csv_to_table(csv_path, table_name, headers=None):
    """Carrega dados de um CSV para uma tabela no banco."""
    try:
        # Limpar os dados do CSV
        logging.info(f"Lendo e limpando o arquivo CSV: {csv_path}")
        df = clean_csv_data(csv_path, headers=headers)

        # Log de quantidade de linhas processadas
        logging.info(f"Linhas a serem carregadas na tabela {table_name}: {len(df)}")

        # Inserir os dados no banco
        logging.info(f"Carregando os dados na tabela {table_name}...")
        with engine.begin() as connection:
            df.to_sql(table_name, con=connection, if_exists='replace', index=False)
        logging.info(f"Dados carregados com sucesso na tabela {table_name}!")

    except Exception as e:
        logging.error(f"Erro ao carregar dados na tabela {table_name}: {e}")

csv_path = "/app/data/df_filtrado.csv"
table_name = "tabua_de_risco"
# Processar e carregar o arquivo filtrado
clean_and_load_filtered_csv(csv_path, table_name, column_mapping)

# Tabelas menores
files_to_tables = {
    "/app/data/arroz.csv": ("arroz", ['localidade', 'unidade', 'jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']),
    "/app/data/milho.csv": ("milho", ['localidade', 'unidade', 'jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']),
    "/app/data/soja.csv": ("soja", ['localidade', 'unidade', 'jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']),
    "/app/data/TRIGO.csv": ("trigo", ['localidade', 'unidade', 'jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']),
    "/app/data/sipeagrofertilizante.csv": ("fertilizantes", ['unidade_federacao', 'municipio', 'numero_registro', 'status_registro', 'cnpj', 'razao_social', 'nome_fantasia', 'area_atuacao', 'atividade', 'classificacao']),
    "/app/data/sigefdeclaracaoareaproducao.csv": ("declaracao_producao", ['tipo_periodo', 'periodo', 'area_total', 'municipio', 'uf', 'especie', 'cultivar', 'area_plantada', 'area_estimada', 'quant_reservada', 'data_plantio']),
    "/app/data/sigefcamposproducaodesementes.csv": ("producao_semente", ['safra', 'especie', 'categoria', 'cultivar', 'municipio', 'uf', 'status', 'data_plantio', 'data_colheita', 'area', 'producao_bruta', 'producao_estimada']),
    "/app/data/sementes.csv": ("semente", ['produto', 'unidade', 'uf', 'ano', 'jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']),
    "/app/data/FERTILIZANTES.csv": ("producao_fertilizantes", ['produto', 'unidade', 'uf', 'ano', 'jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']),
    "/app/data/AGROTOXICO.csv": ("agrotoxico", ['produto', 'unidade', 'uf', 'ano', 'jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']),
    "/app/data/agrofitprodutosformulados.csv": ("registro_agrotoxico", ['nr_registro', 'marca_comercial', 'formulacao', 'ingrediente_ativo', 'titular_de_registro', 'classe', 'modo_de_acao', 'cultura', 'praga_nome_cientifico', 'praga_nome_comum', 'empresa_pais_tipo', 'classe_toxicologica', 'classe_ambiental', 'organicos', 'situacao'])
}

# Processar arquivos menores
for file_path, (table_name, headers) in files_to_tables.items():
    load_csv_to_table(file_path, table_name, headers)