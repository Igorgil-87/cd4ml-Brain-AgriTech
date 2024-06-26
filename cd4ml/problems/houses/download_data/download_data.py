from cd4ml.filenames import get_problem_files
from cd4ml.utils.utils import download_to_file_from_url

baseUri = "https://raw.githubusercontent.com/alura-cursos/continuous-delivery-for-machine-learning-data/main/"

download_params = {
    'url': f"{baseUri}/house_data_100000.csv",
    'url_lookup': f"{baseUri}/zip_lookup.csv"
}


def download(use_cache=True):
    # The simulated house price data
    url = download_params['url']
    file_names = get_problem_files("houses")
    filename = file_names['raw_house_data']

    download_to_file_from_url(url, filename, use_cache=use_cache)

    url = download_params['url_lookup']
    filename = file_names['house_data_zip_lookup']
    download_to_file_from_url(url, filename, use_cache=use_cache)
