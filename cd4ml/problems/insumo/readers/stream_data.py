from csv import DictReader
from cd4ml.filenames import get_problem_files

def stream_data(problem_name):
    """
    Processa os dados do problema insumo.
    """
    file_names = get_problem_files(problem_name)
    filename = file_names['raw_insumo_data']
    return (dict(row) for row in DictReader(open(filename, 'r')))
