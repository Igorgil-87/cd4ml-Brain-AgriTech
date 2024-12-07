def transform_numeric_string(numeric, default_numeric):
    """
    :param numeric: a numeric string or number
    :param default_numeric: default number to use when string cannot be
        cast as numeric
    :return: converted number and Boolean of whether it was successfully cast
        versus defaulted
    """

    is_string = isinstance(numeric, str)
    is_integer = isinstance(numeric, int)
    is_float = isinstance(numeric, float)
    is_bool = isinstance(numeric, bool)

    if is_bool:
        # Don't try to convert Boolean strings like "true"
        numeric = int(numeric)
        is_integer = True

    assert is_string or is_integer or is_float

    if not is_string:
        # return the int or float as is
        return numeric, True

    # try to convert to int or float

    if numeric.isdigit():
        # integer
        return int(numeric), True

    # float
    try:
        numeric_cast = float(numeric)
        return numeric_cast, True

    except ValueError:
        # return default and proper flag
        return default_numeric, False


def transform_stream(stream, numeric_cols, default_numeric=-999,
                     print_failure_stats=True, num_failed=None):

    if num_failed is None:
        # you can pass in an empty dict to retain this info
        num_failed = {}

    for row in stream:
        new_row = {}
        for k, v in row.items():
            if k not in numeric_cols:
                new_row[k] = v
            else:
                numeric, success = transform_numeric_string(v, default_numeric)
                if not success:
                    if k not in num_failed:
                        num_failed[k] = 0

                    num_failed[k] += 1

                new_row[k] = numeric

        yield new_row

    if print_failure_stats:
        print('\nNumber of numeric fields that failed to convert to numeric. Default is %s' % default_numeric)
        for k, v in num_failed.items():
            print("%s: %s" % (k, v))
