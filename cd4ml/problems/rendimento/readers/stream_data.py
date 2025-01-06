import os
from csv import DictReader
from pathlib import Path
from cd4ml.filenames import get_problem_files
from cd4ml.utils.utils import float_or_zero


def stream_raw(problem_name):
    """
    Lê os dados brutos do arquivo rendimento_raw.csv e retorna um gerador.
    """
    # Obtém o caminho do arquivo rendimento_raw.csv
    file_names = get_problem_files(problem_name)
    filename = file_names["rendimento_raw"]

    # Verifica se o arquivo existe
    if not os.path.exists(filename):
        raise FileNotFoundError(f"O arquivo {filename} não foi encontrado.")

    # Exibe as colunas disponíveis no arquivo
    with open(filename, "r") as f:
        reader = DictReader(f)
        print(f"Colunas disponíveis no arquivo: {reader.fieldnames}")

        # Verificar se os campos necessários estão presentes
        schema_path = Path(__file__).parent / "RAW_schema.json"
        categorical_fields, numeric_fields = read_schema_file(schema_path)

        missing_fields = [
            field
            for field in categorical_fields + numeric_fields
            if field not in reader.fieldnames
        ]
        if missing_fields:
            raise ValueError(f"Os seguintes campos estão ausentes no arquivo CSV: {missing_fields}")

    # Retorna um gerador para processar os dados
    return (dict(row) for row in DictReader(open(filename, "r")))


def read_schema_file(schema_path):
    """
    Lê o arquivo de schema JSON e retorna campos categóricos e numéricos.
    """
    import json

    try:
        with open(schema_path, "r") as f:
            schema = json.load(f)

        # Validar estrutura do schema
        if "categorical" not in schema or not isinstance(schema["categorical"], list):
            raise KeyError(f"'categorical' ausente ou não é uma lista no schema: {schema_path}")
        if "numerical" not in schema or not isinstance(schema["numerical"], list):
            raise KeyError(f"'numerical' ausente ou não é uma lista no schema: {schema_path}")

        return schema["categorical"], schema["numerical"]

    except FileNotFoundError:
        raise FileNotFoundError(f"O arquivo de schema não foi encontrado: {schema_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Erro ao decodificar o arquivo JSON: {schema_path}. Detalhes: {e}")


def process_row(row, categorical_fields, numeric_fields):
    """
    Processa uma linha bruta de dados e ajusta ao esquema correto.
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

    
def stream_data(problem_name):
    """
    Processa os dados brutos de acordo com o esquema definido.
    """
    schema_path = Path(Path(__file__).parent, "RAW_schema.json")
    print(f"Carregando schema do arquivo: {schema_path}")
    categorical_fields, numeric_fields = read_schema_file(schema_path)

    print(f"Campos categóricos carregados: {categorical_fields}")
    print(f"Campos numéricos carregados: {numeric_fields}")

    for idx, row in enumerate(stream_raw(problem_name)):
        processed_row = process_row(row, categorical_fields, numeric_fields)
        if idx < 5:  # Apenas para os primeiros 5 registros
            print(f"Linha processada {idx}: {processed_row}")
        yield processed_row


def get_training_validation_filters(params):
    """
    Gera filtros de treino e validação com base nos parâmetros.
    """
    def training_filter(row):
        return params['splitting']['training_random_start'] <= row['split_value'] < params['splitting']['training_random_end']

    def validation_filter(row):
        return params['splitting']['validation_random_start'] <= row['split_value'] < params['splitting']['validation_random_end']

    return training_filter, validation_filter