import os
from csv import DictReader
from cd4ml.filenames import get_problem_files
from cd4ml.utils.utils import float_or_zero

def stream_raw(problem_name):
    """
    Lê os dados brutos do arquivo rendimento_raw.csv.
    """
    from csv import DictReader
    from cd4ml.filenames import get_problem_files

    # Obtém o caminho para o arquivo rendimento_raw.csv
    file_names = get_problem_files(problem_name)
    filename = file_names["rendimento_raw"]

    # Verifica se o arquivo existe
    if not os.path.exists(filename):
        raise FileNotFoundError(f"O arquivo {filename} não foi encontrado.")

    # Log para verificar as primeiras linhas do arquivo
    with open(filename, "r") as f:
        reader = DictReader(f)
        for i, row in enumerate(reader):
            print(f"Linha {i}: {row}")
            if i >= 5:  # Mostrar apenas as primeiras 5 linhas
                break

    # Retorna um generator para iterar sobre os dados
    return (dict(row) for row in DictReader(open(filename, "r")))

def read_schema_file(schema_path):
    """
    Lê o arquivo de schema JSON e retorna campos categóricos e numéricos.
    """
    import json

    try:
        with open(schema_path, "r") as f:
            schema = json.load(f)

        # Verificar se as chaves categóricas e numéricas estão presentes
        if "categorical" not in schema:
            raise KeyError(f"A chave 'categorical' está ausente no schema: {schema_path}")
        if "numeric" not in schema:
            raise KeyError(f"A chave 'numeric' está ausente no schema: {schema_path}")

        categorical_fields = schema["categorical"]
        numeric_fields = schema["numeric"]

        return categorical_fields, numeric_fields

    except FileNotFoundError:
        raise FileNotFoundError(f"O arquivo de schema não foi encontrado: {schema_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Erro ao decodificar o arquivo JSON: {schema_path}. Detalhes: {e}")


def stream_data(problem_name):
    """
    Processa os dados brutos de acordo com o esquema definido.
    """
    from cd4ml.problems import read_schema_file
    from pathlib import Path

    schema_path = Path(Path(__file__).parent, "RAW_schema.json")
    print(f"Carregando schema do arquivo: {schema_path}")
    categorical_fields, numeric_fields = read_schema_file(schema_path)

    print(f"Campos categóricos carregados: {categorical_fields}")
    print(f"Campos numéricos carregados: {numeric_fields}")

    return (process_row(row, categorical_fields, numeric_fields) for row in stream_raw(problem_name))

    
def process_row(row, categorical_fields, numeric_fields):
    """
    Processa uma linha bruta de dados e ajusta ao esquema correto.
    """
    row_out = {k: row[k] for k in categorical_fields}

    for field in numeric_fields:
        row_out[field] = float_or_zero(row[field])

    # Adiciona uma coluna 'split_value' para divisão dos dados (ajuste se necessário)
    row_out["split_value"] = float(row.get("split", 0))  # Substituir conforme o formato do dataset
    return row_out

def get_training_validation_filters(params):
    """
    Gera filtros de treino e validação com base nos parâmetros.
    """
    def training_filter(row):
        return params['splitting']['training_random_start'] <= row['split_value'] < params['splitting']['training_random_end']

    def validation_filter(row):
        return params['splitting']['validation_random_start'] <= row['split_value'] < params['splitting']['validation_random_end']

    return training_filter, validation_filter