"""
Reservoir sampling. Sample from stream of unknown length

usage:

from statistics import median

res = initialize_res_samples(fields)
num_samples = 50

random_generator = random.Random()
random_generator.seed(42)

for row_index, row in enumerate(stream):
    for field in fields:
        value = row[field]

    update_res_samples(res_samples, row_index, field, value, num_samples, random_generator)

medians = {field: median(res_samples[field] for field in fields}
"""


def initialize_res_samples(fields):
    return {field: [] for field in fields}


def update_res_samples(res_samples, row_index, field, value, num_samples, random_generator):
    """
    Update reservoir samples
    :param res_samples: dicts of lists, instantiated with initialize_res_samples
    :param row_index: the index in the stream
    :param field: field that is being updated
    :param value: value for this field in this row
    :param num_samples: number of samples to keep for each field
    :param random_generator: random.Random() instance, be sure to set seed
    :return:
    """
    if row_index < num_samples:
        res_samples[field].append(value)
    else:
        probability = num_samples/(row_index + 1)
        ramdom_number = random_generator.random()
        if ramdom_number < probability:
            index = random_generator.randint(0, num_samples - 1)
            res_samples[field][index] = value
