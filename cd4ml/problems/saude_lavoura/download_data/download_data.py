from cd4ml.filenames import get_problem_files
from cd4ml.utils.utils import download_to_file_from_url

download_params = {
    'url': "https://raw.githubusercontent.com/"
    "alura-cursos/continuous-delivery-for-machine-learning-data/main/"
    "iris.csv"  # Altere o nome do arquivo e a URL, se necessário, para saude_lavoura.
}


def download(use_cache=False):
    # The simulated data for saude_lavoura
    url = download_params['url']
    file_names = get_problem_files("saude_lavoura")  # Substituído 'iris' por 'saude_lavoura'
    filename = file_names['raw_iris_data']  # Substitua 'raw_iris_data' pelo novo identificador, como 'raw_saude_lavoura_data'

    download_to_file_from_url(url, filename, use_cache=use_cache)