from csv import DictReader
from cd4ml.filenames import get_problem_files


def get_region_lookup(problem_name):
    file_names = get_problem_files(problem_name)
    filename = file_names["commodities_regions_lookup"]
    return {row["region_id"]: row for row in DictReader(open(filename, "r"))}
