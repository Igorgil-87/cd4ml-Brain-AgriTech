from csv import DictReader
from cd4ml.filenames import get_problem_files
from cd4ml.utils.utils import float_or_zero


def stream_raw(problem_name):
    """
    Lê os dados brutos do arquivo rendimento_raw.csv.
    """
    # Obtém o caminho para o arquivo rendimento_raw.csv
    file_names = get_problem_files(problem_name)
    filename = file_names["rendimento_raw"]
    
    # Verifica se o arquivo existe
    if not os.path.exists(filename):
        raise FileNotFoundError(f"O arquivo {filename} não foi encontrado.")
    
    # Retorna um generator para iterar sobre os dados
    return (dict(row) for row in DictReader(open(filename, "r")))


def stream_data(problem_name):
    """
    Processa os dados brutos de acordo com o esquema definido.
    """
    from cd4ml.problems import read_schema_file
    from pathlib import Path

    # Lê o esquema JSON (definido em RAW_schema.json)
    categorical_fields, numeric_fields = read_schema_file(Path(Path(__file__).parent, "RAW_schema.json"))

    # Processa cada linha dos dados brutos
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