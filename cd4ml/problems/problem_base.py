from time import time
import numpy as np
from cd4ml.get_encoder import get_trained_encoder
from cd4ml.logger.fluentd_logging import FluentdLogger
from cd4ml.model_tracking import tracking
from cd4ml.model_tracking.validation_metrics import get_validation_metrics
from cd4ml.utils.problem_utils import Specification
from cd4ml.ml_model import MLModel
from cd4ml.feature_importance import get_feature_importance
from cd4ml.splitter import splitter
from cd4ml.model_tracking.validation_plots import get_validation_plot
from cd4ml.utils.utils import get_uuid
from pathlib import Path
import json

import logging
logger = logging.getLogger(__name__)


class ProblemBase:
    """
    Generic Problem Interface for Problems
    Implementation needs to add various data elements and methods
    """

    def __init__(self,
                 problem_name,
                 data_downloader='default',
                 ml_pipeline_params_name='default',
                 feature_set_name='default',
                 algorithm_name='default',
                 algorithm_params_name='default'):

        self.model_id = get_uuid()
        self.logger = logging.getLogger(__name__)
        self.fluentd_logger = FluentdLogger()

        self.data_downloader = data_downloader
        self.problem_name = problem_name
        self.feature_set_name = feature_set_name
        self.ml_pipeline_params_name = ml_pipeline_params_name
        self.algorithm_name = algorithm_name
        self.algorithm_params_name = algorithm_params_name
        self.ml_pipeline_params = self.get_ml_pipeline_params(ml_pipeline_params_name)

        self.logger.info("Created model_id: %s" % self.model_id)

        if algorithm_name == 'default':
            self.resolved_algorithm_name = self.ml_pipeline_params['default_algorithm']
        else:
            self.resolved_algorithm_name = algorithm_name

        self.specification = self.make_specification()

        self._stream_data = None
        self.training_filter = None
        self.validation_filter = None
        self.get_validation_metrics = None

        self.trained_model = None
        self.validation_metrics = None
        self.encoder = None
        self.ml_model = None
        self.tracker = None
        self.feature_data = None
        self.importance = None

        self.training_filter, self.validation_filter = splitter(self.ml_pipeline_params)

        feature_set_class = self.get_feature_set_constructor(feature_set_name)

        self.feature_set = feature_set_class(self.ml_pipeline_params['identifier_field'],
                                             self.ml_pipeline_params['target_field'],
                                             {})

        self.algorithm_params = self.get_algorithm_params(self.resolved_algorithm_name,
                                                          self.algorithm_params_name)

    def stream_processed(self):
        self.logger.info(f"Processed stream contains {len(processed)} rows.")

        """
        Gera o fluxo de dados processados, garantindo que todas as chaves obrigatórias existam.
        """
        required_keys = [
            'Cultura',
            'Área colhida (ha)',
            'Valor da Produção Total',
            'Rendimento médio (kg/ha)',  # Incluindo o campo faltante
        ]

        def ensure_keys(row):
            for key in required_keys:
                if key not in row:
                    self.logger.warning(f"Campo ausente '{key}' detectado nos dados processados. Adicionando valor padrão.")
                    row[key] = 0.0 if key != 'Cultura' else 'Indefinido'  # Adiciona valores padrão
            return row

        return (ensure_keys(row) for row in self._stream_data(self.problem_name))

    def stream_features(self):
        """
        Generates processed features, ensuring required keys are present.
        """
        required_keys = ['Área colhida (ha)', 'Valor da Produção Total', 'cultura']
        for processed_row in self.stream_processed():
            missing_keys = [key for key in required_keys if key not in processed_row]
            if missing_keys:
                self.logger.warning(f"Missing keys detected: {missing_keys}. Adding default values.")
                for key in missing_keys:
                    processed_row[key] = 0.0  # Default value for missing fields
            yield self.feature_set.features(processed_row)

    def prepare_feature_data(self):
        pass

    def get_encoder(self, write=False, read_from_file=False):
        """
        Obtém ou cria o encoder para os dados do problema.
        """
        self.prepare_feature_data()

        start = time()
        ml_fields = self.feature_set.ml_fields()
        omitted = self.feature_set.params['encoder_untransformed_fields']

        self.encoder = get_trained_encoder(
            self.stream_features(),
            ml_fields,
            self.problem_name,
            write=write,
            read_from_file=read_from_file,
            base_features_omitted=omitted
        )

        # Garantir que todas as chaves necessárias existam antes de adicionar estatísticas numéricas
        def ensure_keys(row, required_keys):
            for key in required_keys:
                if key not in row:
                    self.logger.warning(f"Adicionando chave ausente '{key}' com valor padrão 0.0")
                    row[key] = 0.0
            return row

        # Validação para `add_numeric_stats`
        try:
            required_keys = ['Área colhida (ha)', 'Valor da Produção Total', 'cultura']
            validated_stream = (ensure_keys(row, required_keys) for row in self.stream_features())
            self.encoder.add_numeric_stats(validated_stream)
        except KeyError as e:
            self.logger.error(f"KeyError durante a adição de estatísticas numéricas: {e}")
            raise

        runtime = time() - start
        self.logger.info('Encoder time: {0:.1f} seconds'.format(runtime))


    def training_stream(self):
        """
        Gera o fluxo de treinamento, garantindo que os campos obrigatórios existam.
        """
        required_keys = ['Cultura', 'Área colhida (ha)', 'Valor da Produção Total']  # Adicione todos os campos obrigatórios aqui.

        def ensure_keys(row):
            for key in required_keys:
                if key not in row:
                    self.logger.warning(f"Campo ausente '{key}' detectado no treinamento. Adicionando valor padrão.")
                    row[key] = 'Indefinido' if key == 'Cultura' else 0.0  # Valor padrão para campos ausentes.
            return row

        return (ensure_keys(row) for row in self.stream_processed() if self.training_filter(row))


    def validation_stream(self):
        filtered_data = [row for row in self.stream_processed() if self.validation_filter(row)]
        self.logger.info(f"Validation stream contains {len(filtered_data)} rows.")
        return iter(filtered_data)

    def train(self):
        if self.ml_model is not None:
            self.logger.warning('Model is already trained, cannot retrain')
            return

        self.logger.info('Starting training')
        start = time()
        if self.encoder is None:
            self.get_encoder()

        self.ml_model = MLModel(self.specification.spec['algorithm_name_actual'],
                                self.algorithm_params,
                                self.feature_set,
                                self.encoder,
                                self.ml_pipeline_params['training_random_seed'])

        if self.tracker:
            self.tracker.log_algorithm_params(self.algorithm_params)

        self.ml_model.train(self.training_stream())

        model_name = self.specification.spec['algorithm_name_actual']
        self.importance = get_feature_importance(self.ml_model.trained_model, model_name, self.encoder)

        runtime = time() - start
        self.logger.info('Training time: {0:.1f} seconds'.format(runtime))


def validate(self):
    self.logger.info('Starting validation')
    true_validation_target = list(self.true_target_stream(self.validation_stream()))
    self.logger.info(f"Number of validation targets: {len(true_validation_target)}")
    validation_prediction = list(self.ml_model.predict_processed_rows(self.validation_stream()))

    if not true_validation_target:
        self.logger.error("O conjunto de validação está vazio. Verifique os dados de entrada ou os filtros.")
        raise ValueError("O conjunto de validação está vazio. Não é possível calcular métricas de validação.")

    if self.ml_model.model_type == 'classifier':
        validation_pred_prob = np.array(list(self.ml_model.predict_processed_rows(self.validation_stream(), prob=True)))
        target_levels = self.ml_model.trained_model.classes_
    elif self.ml_model.model_type == 'regressor':
        validation_pred_prob = None
        target_levels = None
    else:
        raise ValueError('Unknown classification type: %s' % self.ml_model.model_type)

    logger.info('Done with predictions')

    # Calcular métricas de validação
    self.logger.info('Calculating validation metrics')
    validation_metric_names = self.ml_pipeline_params['validation_metric_names']

    try:
        self.validation_metrics = get_validation_metrics(validation_metric_names,
                                                         true_validation_target,
                                                         validation_prediction,
                                                         validation_pred_prob,
                                                         target_levels)
    except Exception as e:
        self.logger.error(f"Erro ao calcular métricas de validação: {e}")
        raise

    self.logger.info('Validation completed successfully')
    runtime = time() - start
    self.logger.info('Validation time: {0:.1f} seconds'.format(runtime))




    def true_target_stream(self, stream):
        target_name = self.feature_set.target_field
        return (row[target_name] for row in stream)

    def write_ml_model(self):
        self.tracker.log_model(self.ml_model)

    def setup_tracker(self):
        self.tracker = tracking.Track(self.model_id, self.specification.spec)

    def run_all(self):
        start = time()
        self.setup_tracker()
        self.tracker.log_ml_pipeline_params(self.ml_pipeline_params)
        self.download_data()
        self.get_encoder()
        self.train()
        self.write_ml_model()
        self.validate()

        runtime = time() - start
        self.tracker.save_results()

        self.logger.info('All ML steps time: {0:.1f} seconds'.format(runtime))
        self.logger.info('Finished model: %s' % self.model_id)

    def download_data(self):
        raise ValueError("This function should be implemented in a parent class")

    @staticmethod
    def get_feature_set_constructor(feature_set_name):
        raise NotImplementedError("This function should be implemented in a parent class")

    def get_ml_pipeline_params(self, ml_pipeline_params_name):
        path = Path(Path(__file__).parent, self.problem_name, 'ml_pipelines', f"{ml_pipeline_params_name}.json")
        if not path.exists():
            self.logger.error(f"The file {path} does not exist.")
            raise FileNotFoundError(f"The expected file {path} does not exist. Check the project structure.")
        return self.read_json_file_for_current_problem_as_dict(path)

    def get_algorithm_params(self, algorithm_name, algorithm_params_name):
        path = f'algorithms/{algorithm_name}/{algorithm_params_name}.json'
        return self.read_json_file_for_current_problem_as_dict(path)

    def make_specification(self):
        return Specification(self.problem_name,
                             self.data_downloader,
                             self.ml_pipeline_params_name,
                             self.feature_set_name,
                             self.algorithm_name,
                             self.algorithm_params_name,
                             self.resolved_algorithm_name)

    def read_json_file_for_current_problem_as_dict(self, file_path):
        path = Path(Path(__file__).parent, self.problem_name, file_path)

        try:
            with open(path, "r") as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error loading JSON file: {file_path}. Check if it is well-formatted.") from e
        except FileNotFoundError:
            raise FileNotFoundError(f"The expected file {file_path} was not found. Check the path.")

    def __repr__(self):
        messages = ['Problem']
        for k, v in self.__dict__.items():
            if v is None:
                continue
            if str(v.__class__) == "<class 'function'>":
                continue
            messages.append("%s: \n%s\n" % (k, v))

        return '\n'.join(messages)