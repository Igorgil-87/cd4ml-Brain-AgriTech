import json
from random import Random
from wickedhot import one_hot_encode as ohe
from wickedhot.form_generator import encoder_package_to_form_elements, encoder_package_to_html_page
from wickedhot.transform_stream import transform_stream


class OneHotEncoder:
    def __init__(self, categorical_cols, numeric_cols, max_levels_default=10000,
                 omit_cols=None, default_numeric=-999):

        assert max_levels_default > 0
        self.max_levels_default = max_levels_default
        self.numeric_cols = numeric_cols
        self.omit_cols = omit_cols
        self.one_hot_encoder_dicts = None
        self.encoder = None
        self.decoder = None
        self.index_lookup = None
        self.numeric_stats = None
        self.failed_numeric_conversion_stats = {}
        self.default_numeric = default_numeric
        self.encoded_stream_failed_numeric_conversion_stats = {}

        if isinstance(categorical_cols, list):
            self.categorical_n_levels_dict = {k: self.max_levels_default for k in categorical_cols}
        elif isinstance(categorical_cols, dict):
            if len(categorical_cols) > 0:
                assert min(list(categorical_cols.values())) > 0
            self.categorical_n_levels_dict = categorical_cols
        else:
            raise ValueError('categorical_cols must be a list or dictionary')

    def _transform_stream(self, stream_of_dicts):
        return transform_stream(stream_of_dicts,
                                self.numeric_cols,
                                num_failed=self.failed_numeric_conversion_stats,
                                default_numeric=self.default_numeric)

    def _transform_row(self, row):
        result = transform_stream([row],
                                  self.numeric_cols,
                                  default_numeric=self.default_numeric,
                                  num_failed=self.encoded_stream_failed_numeric_conversion_stats)
        result = list(result)
        assert len(result) == 1
        return result[0]

    def load_from_data_stream(self, stream_of_dicts):
        stream_of_dicts = self._transform_stream(stream_of_dicts)

        self.one_hot_encoder_dicts = ohe.get_one_hot_encoder_dicts_from_data_stream(stream_of_dicts,
                                                                                    self.categorical_n_levels_dict)
        self._get_encoder_decoder()

    def add_numeric_stats(self, stream_of_dicts):
        # reset this
        self.failed_numeric_conversion_stats = {}

        stream_of_dicts = self._transform_stream(stream_of_dicts)

        random_generator = Random()
        random_generator.seed(265472)

        self.numeric_stats = ohe.get_numeric_stats(stream_of_dicts, self.numeric_cols, random_generator)

    def package_data(self):
        data = {'max_levels_default': self.max_levels_default,
                'numeric_cols': self.numeric_cols,
                'categorical_n_levels_dict': self.categorical_n_levels_dict,
                'one_hot_encoder_dicts': self.one_hot_encoder_dicts,
                'numeric_stats': self.numeric_stats,
                'omit_cols': self.omit_cols,
                'default_numeric': self.default_numeric,
                'failed_numeric_conversion_stats': self.failed_numeric_conversion_stats}

        return data

    def save(self, json_file_name):
        with open(json_file_name, 'w') as fp:
            json.dump(self.package_data(), fp)

    def load_from_packaged_data(self, data_object):
        self.max_levels_default = data_object['max_levels_default']
        self.numeric_cols = data_object['numeric_cols']
        self.categorical_n_levels_dict = data_object['categorical_n_levels_dict']
        self.one_hot_encoder_dicts = data_object['one_hot_encoder_dicts']
        self.numeric_stats = data_object['numeric_stats']
        self.omit_cols = data_object['omit_cols']
        self.default_numeric = data_object['default_numeric']
        self.failed_numeric_conversion_stats = data_object['failed_numeric_conversion_stats']

        self._get_encoder_decoder()

    def load_from_file(self, json_file_name):
        with open(json_file_name, 'r') as fp:
            packaged_data = json.load(fp)

        self.load_from_packaged_data(packaged_data)

    def _get_encoder_decoder(self):
        self.index_lookup = ohe.get_key_val_pair_to_index_lookup(self.one_hot_encoder_dicts,
                                                                 self.numeric_cols,
                                                                 omit_keys=self.omit_cols)

        self.index_lookup_rev = {v: k for k, v in self.index_lookup.items()}
        self.encoder, self.decoder = ohe.get_line_encoder_and_decoder(self.index_lookup)

    def encode_row(self, row):
        row_transformed = self._transform_row(row)
        return self.encoder(row_transformed)

    def decode_row(self, row):
        return self.decoder(row)

    def index_to_column(self, index):
        return self.index_lookup_rev[index]

    def get_index(self, x):
        if isinstance(x, tuple):
            key, value = x
        elif isinstance(x, str):
            key = x
            value = None
        else:
            raise ValueError('x must be a string for numeric col of key value pair for categorical level')

        idx, _ = ohe.get_index(key, value, self.index_lookup)
        return idx

    def encode_data_stream(self, stream):
        # generator

        # reset this
        self.encoded_stream_failed_numeric_conversion_stats = {}
        return (self.encode_row(row) for row in stream)

    def encode_data(self, stream):
        return list(self.encode_data_stream(stream))

    def decode_data_stream(self, encoded_data_stream):
        return (self.decode_row(row) for row in encoded_data_stream)

    def decode_data(self, encoded_data_stream):
        return list(self.decode_data_stream(encoded_data_stream))

    def get_form_html_elements(self, post_url=None, initial_values=None,
                               extra_numerics=None,
                               extra_categoricals=None,
                               omitted_fields=None):
        """
        Get html header text and form div text to be injected into an html page
        via templating (in the header section and body respectively)
        :param post_url: url that form will be submitted to on submission
        :param initial_values: dict of initial values for form, otherwise , it chooses
            them by itself
        :param extra_numerics: extra numeric fields to add
        :param extra_categoricals: extra categorical fields to add
        :param omitted_fields: fields to omit
        :return: html_header, div_text
        """
        return encoder_package_to_form_elements(self.package_data(),
                                                post_url=post_url,
                                                initial_values=initial_values,
                                                extra_numerics=extra_numerics,
                                                extra_categoricals=extra_categoricals,
                                                omitted_fields=omitted_fields)

    def get_form_html_page(self, post_url=None, initial_values=None,
                           extra_numerics=None,
                           extra_categoricals=None,
                           omitted_fields=None):
        """
        Return entire functioning html page using the default simple index.html template
        :param post_url: url that form will be submitted to on submission
        :param initial_values: dict of initial values for form, otherwise , it chooses
            them by itself
        :param extra_numerics: extra numeric fields to add
        :param extra_categoricals: extra categorical fields to add
        :param omitted_fields: fields to omit
        :return:
        """
        return encoder_package_to_html_page(self.package_data(),
                                            post_url=post_url,
                                            initial_values=initial_values,
                                            extra_numerics=extra_numerics,
                                            extra_categoricals=extra_categoricals,
                                            omitted_fields=omitted_fields)
