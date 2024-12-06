from cd4ml.filenames import get_problem_files
from cd4ml.utils.utils import download_to_file_from_url

base_uri = "https://example.com/agriculture_data"

download_params = {
    "url_data": f"{base_uri}/commodities_data.csv",
    "url_regions": f"{base_uri}/regions.csv"
}


def download(use_cache=True):
    # Baixar dados principais
    url = download_params["url_data"]
    file_names = get_problem_files("commodities")
    filename = file_names["raw_commodities_data"]

    download_to_file_from_url(url, filename, use_cache=use_cache)

    # Baixar informações regionais
    url = download_params["url_regions"]
    filename = file_names["commodities_regions_lookup"]
    download_to_file_from_url(url, filename, use_cache=use_cache)
