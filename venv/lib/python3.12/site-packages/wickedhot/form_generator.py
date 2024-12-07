from wickedhot.one_hot_encode import unknown_level_value
from wickedhot.html_form import form_data_to_form_elements, form_data_to_html_page

LEVELS_MAX_FOR_DROP_DOWN = 500


def process_extras(extra_numerics, extra_categoricals, omitted_fields):
    if omitted_fields is None:
        omitted_fields = []

    if extra_numerics is None:
        extra_numerics = {}
    else:
        extra_numerics = {k: v for k, v in extra_numerics.items() if k not in omitted_fields}

    if extra_categoricals is None:
        extra_categoricals = {}
    else:
        extra_categoricals = {k: v for k, v in extra_categoricals.items()
                              if k not in omitted_fields}
        for k, v in extra_categoricals.items():
            if unknown_level_value not in v:
                v.append(unknown_level_value)

    return extra_numerics, extra_categoricals, omitted_fields


def encoder_package_to_schema(encoder_package,
                              extra_numerics=None,
                              extra_categoricals=None,
                              omitted_fields=None):

    extra_numerics, extra_categoricals, omitted_fields = process_extras(extra_numerics,
                                                                        extra_categoricals,
                                                                        omitted_fields)
    properties = {}
    stats = encoder_package['numeric_stats']

    # numerics
    numeric_fields = encoder_package['numeric_cols'] + list(extra_numerics.keys())

    for field in numeric_fields:
        if field in omitted_fields:
            continue

        properties[field] = {
            "type": "number",
            "title": field.capitalize(),
            "required": True
        }

        if stats is not None:
            if field in stats:
                pass
                # properties[field]['minimum'] = stats[field]['min']
                # properties[field]['maximum'] = stats[field]['max']

    # categoricals

    encoder_dicts = encoder_package['one_hot_encoder_dicts']

    for field, value_dicts in encoder_dicts.items():
        if field in omitted_fields:
            continue

        values = sorted(value_dicts.items(), key=lambda x: x[1])
        levels = [v[0] for v in values]
        n_levels = len(levels)
        levels = levels + [unknown_level_value]

        properties[field] = {
            "type": "string",
            "title": field.capitalize(),
            "required": True
        }

        if n_levels < LEVELS_MAX_FOR_DROP_DOWN:
            properties[field]["enum"] = levels

    for field, levels in extra_categoricals.items():
        properties[field] = {
            "type": "string",
            "title": field.capitalize(),
            "required": True,
            "enum": levels
        }

    schema = {
        "title": "Input features",
        "description": "Enter features",
        "type": "object",
        "properties": properties
    }

    return schema


def encoder_package_to_options(encoder_package, post_url=None,
                               extra_numerics=None,
                               extra_categoricals=None,
                               omitted_fields=None):
    """
    :param encoder_package: one hot encoder package
    :param post_url: url to send form data to on submission
        default is ''
        for testing purposes, you may use PUBLIC and it will use
        "http://httpbin.org/post" which prints the result
        this is not secure so don't do that with sensitive data
    :return:
    """

    extra_numerics, extra_categoricals, omitted_fields = process_extras(extra_numerics,
                                                                        extra_categoricals,
                                                                        omitted_fields)

    if post_url is None:
        post_url = ''

    if post_url == 'PUBLIC':
        post_url = "http://httpbin.org/post"

    fields = {}

    numeric_cols = encoder_package['numeric_cols'] + list(extra_numerics.keys())

    for field in numeric_cols:
        if field in omitted_fields:
            continue

        fields[field] = {
            "size": 20
        }

    encoder_dicts = encoder_package['one_hot_encoder_dicts']

    for field, value_dicts in encoder_dicts.items():
        if field in omitted_fields:
            continue

        values = sorted(value_dicts.items(), key=lambda x: x[1])
        levels = [v[0] for v in values]

        n_levels = len(levels)

        levels = levels + [unknown_level_value]

        if n_levels < LEVELS_MAX_FOR_DROP_DOWN:
            fields[field] = {
                "type": "select",
                "optionLabels": levels,
                "sort": False}
        else:
            fields[field] = {"size": 20}

    for field, levels in extra_categoricals.items():
        fields[field] = {
            "type": "select",
            "optionLabels": levels,
            "sort": False
        }

    options = {
        "form": {
            "attributes": {
                "action": post_url,
                "method": "post"
            },
            "buttons": {
                "submit": {}
            }
        },
        "helper": "Hit submit to update the prediction",
        "fields": fields}

    return options


def encoder_package_to_form_data(encoder_package, post_url=None,
                                 extra_numerics=None,
                                 extra_categoricals=None,
                                 omitted_fields=None):
    """
    Generate the form
    :param encoder_package: encoder package dict
    :param post_url: url to send form data to on submission
        default is ''
        for testing purposes, you may use PUBLIC and it will use
        "http://httpbin.org/post" which prints the result
        this is not secure so don't do that with sensitive data
    :return: form data
    """

    schema = encoder_package_to_schema(encoder_package,
                                       extra_numerics=extra_numerics,
                                       extra_categoricals=extra_categoricals,
                                       omitted_fields=omitted_fields)

    options = encoder_package_to_options(encoder_package, post_url=post_url,
                                         extra_numerics=extra_numerics,
                                         extra_categoricals=extra_categoricals,
                                         omitted_fields=omitted_fields)

    extra_numerics, extra_categoricals, omitted_fields = process_extras(extra_numerics,
                                                                        extra_categoricals,
                                                                        omitted_fields)

    stats = encoder_package['numeric_stats']

    def default_value(stats, field):
        value = stats[field]['median']
        if abs(value) > 1000:
            value = int(value)
        return value

    if stats is None:
        data = {field: 0 for field in encoder_package['numeric_cols'] if field not in omitted_fields}
    else:
        data = {field: float("%0.2f" % default_value(stats, field))
                for field in encoder_package['numeric_cols']
                if field not in omitted_fields}

    for field, default in extra_numerics.items():
        data[field] = default

    form_data = {"schema": schema,
                 "options": options,
                 "view": "bootstrap-edit",
                 "data": data}

    return form_data


def encoder_package_to_form_elements(encoder_package, post_url=None, initial_values=None,
                                     extra_numerics=None,
                                     extra_categoricals=None,
                                     omitted_fields=None):

    form_data = encoder_package_to_form_data(encoder_package, post_url=post_url,
                                             extra_numerics=extra_numerics,
                                             extra_categoricals=extra_categoricals,
                                             omitted_fields=omitted_fields)

    if initial_values is not None:
        form_data['data'] = initial_values

    header_text, form_div = form_data_to_form_elements(form_data)
    return header_text, form_div


def encoder_package_to_html_page(encoder_package, post_url=None, initial_values=None,
                                 extra_numerics=None,
                                 extra_categoricals=None,
                                 omitted_fields=None):

    form_data = encoder_package_to_form_data(encoder_package, post_url=post_url,
                                             extra_numerics=extra_numerics,
                                             extra_categoricals=extra_categoricals,
                                             omitted_fields=omitted_fields)
    if initial_values is not None:
        form_data['data'] = initial_values

    return form_data_to_html_page(form_data)
