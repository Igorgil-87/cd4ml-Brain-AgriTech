import pandas as pd
import logging
import chardet


# Configurar o log
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Função para detectar a codificação
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(10000))  # Detecta com base nos primeiros 10KB
        return result['encoding']




def load_producao_semente(engine, file_path="/app/data/sigefcamposproducaodesementes.csv"):
    table_name = "producao_semente"
    headers = ['safra', 'especie', 'categoria', 'cultivar', 'municipio', 'uf', 'status', 
               'data_plantio', 'data_colheita', 'area', 'producao_bruta', 'producao_estimada']

    # Mapeamento de nomes de colunas do arquivo para os nomes esperados no banco de dados
    column_mapping = {
        'Safra': 'safra',
        'Especie': 'especie',
        'Categoria': 'categoria',
        'Cultivar': 'cultivar',
        'Municipio': 'municipio',
        'UF': 'uf',
        'Status': 'status',
        'Data do Plantio': 'data_plantio',
        'Data de Colheita': 'data_colheita',
        'Area': 'area',
        'Producao bruta': 'producao_bruta',
        'Producao estimada': 'producao_estimada'
    }

    try:
        # Detectar a codificação do arquivo
        encoding = detect_encoding(file_path)
        logging.info(f"Detectada a codificação do arquivo {file_path}: {encoding}")

        # Ler o arquivo CSV
        df = pd.read_csv(file_path, sep=';', encoding=encoding, on_bad_lines='skip')


        # Renomear colunas para corresponder ao esperado
        df.rename(columns=column_mapping, inplace=True)

        # Verificar se todas as colunas necessárias estão presentes
        missing_headers = [col for col in headers if col not in df.columns]
        if missing_headers:
            logging.error(f"Colunas ausentes no arquivo: {missing_headers}")
            return

        # Selecionar somente as colunas esperadas
        df = df[headers]

        # Converter valores
        df['area'] = pd.to_numeric(df['area'], errors='coerce')
        df['data_plantio'] = pd.to_datetime(df['data_plantio'], errors='coerce', dayfirst=True)
        df['data_colheita'] = pd.to_datetime(df['data_colheita'], errors='coerce', dayfirst=True)

        # Inserir no banco
        with engine.begin() as connection:
            df.to_sql(table_name, con=connection, if_exists='append', index=False)

        logging.info(f"Tabela {table_name} carregada com sucesso!")
    except Exception as e:
        logging.error(f"Erro ao carregar a tabela {table_name}: {e}")