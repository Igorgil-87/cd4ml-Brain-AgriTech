import json
import os
from jinja2 import Template


def get_templates_text():
    template_dir = os.path.realpath(os.path.dirname(__file__) + '/templates')
    template_files = {'alpaca_index': 'alpaca_index.html',
                      'alpaca_form': 'alpaca_form.html',
                      'alpaca_header': 'alpaca_header.html',
                      'alpaca_example_data': 'alpaca_example.json'}

    paths = {key: "%s/%s" % (template_dir, file) for key, file in template_files.items()}
    templates = {key: open(filename, 'r').read() for key, filename in paths.items()}
    return templates


def form_data_to_form(form_data, templates):
    alpaca_json_data = json.dumps(form_data, indent=2)
    template = Template(templates['alpaca_form'])
    return template.render(alpaca_json_data=alpaca_json_data)


def form_data_to_form_elements(form_data):
    templates = get_templates_text()

    if form_data is None:
        templates_text = templates['alpaca_example_data']
        form_data = json.loads(templates_text)

    header_text = templates['alpaca_header']
    form_div = form_data_to_form(form_data, templates)

    return header_text, form_div


def form_data_to_html_page(form_data):
    header_text, form_div = form_data_to_form_elements(form_data)
    index_text = get_templates_text()['alpaca_index']
    index = Template(index_text)
    return index.render(alpaca_header=header_text, form_div=form_div)
