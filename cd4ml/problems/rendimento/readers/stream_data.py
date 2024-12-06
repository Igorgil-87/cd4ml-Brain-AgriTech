from csv import DictReader
from cd4ml.filenames import get_problem_files
from cd4ml.utils.utils import float_or_zero


def stream_raw(problem_name):
    """
    Retorna os dados brutos do problema.
    :param problem_name: Nome do problema
    :return: Gerador de linhas de dados brutos
    """
    file_names = get_problem_files(problem_name)
    filename = file_names['raw_rendimento_data']
    return (dict(row) for row in DictReader(open(filename, 'r')))


def stream_data(problem_name):
    """
    Processa os dados brutos e retorna linhas de dados processados.
    :param problem_name: Nome do problema
    :return: Gerador de linhas de dados processados
    """
    from cd4ml.problems import read_schema_file
    from pathlib import Path
    categorical_fields, numeric_fields = read_schema_file(Path(Path(__file__).parent, "raw_schema.json"))

    return (process_row(row, categorical_fields, numeric_fields) for row in stream_raw(problem_name))


def process_row(row, categorical_fields, numeric_fields):
    """
    Processa uma linha de dados brutos e aplica o esquema.
    :param row: Linha de dados brutos
    :param categorical_fields: Campos categóricos
    :param numeric_fields: Campos numéricos
    :return: Linha de dados processados
    """
    row_out = {k: row[k] for k in categorical_fields}

    for field in numeric_fields:
        row_out[field] = float_or_zero(row[field])

    return row_out
