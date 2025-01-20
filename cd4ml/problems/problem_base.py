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

# Configuração de logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ProblemBase:
    """
    Interface base para problemas de machine learning.
    """

    def __init__(self, problem_name, data_downloader='default', ml_pipeline_params_name='default',
                 feature_set_name='default', algorithm_name='default', algorithm_params_name='default'):
        logger.info(f"Inicializando ProblemBase para o problema: {problem_name}")
        self.model_id = get_uuid()
        logger.info(f"ID do modelo gerado: {self.model_id}")

        # Atributos principais
        self.problem_name = problem_name
        self.data_downloader = data_downloader
        self.feature_set_name = feature_set_name
        self.ml_pipeline_params_name = ml_pipeline_params_name
        self.algorithm_name = algorithm_name
        self.algorithm_params_name = algorithm_params_name
        self.fluentd_logger = FluentdLogger()

        # Carregar parâmetros do pipeline
        self.ml_pipeline_params = self.get_ml_pipeline_params(ml_pipeline_params_name)
        self.resolved_algorithm_name = algorithm_name if algorithm_name != 'default' else self.ml_pipeline_params.get('default_algorithm')
        self.specification = self.make_specification()

        # Divisão e conjunto de features
        self.training_filter, self.validation_filter = splitter(self.ml_pipeline_params)
        feature_set_class = self.get_feature_set_constructor(feature_set_name)
        self.feature_set = feature_set_class(self.ml_pipeline_params['identifier_field'],
                                             self.ml_pipeline_params['target_field'], {})

        # Parâmetros do algoritmo
        self.algorithm_params = self.get_algorithm_params(self.resolved_algorithm_name, self.algorithm_params_name)

        # Inicializações adicionais
        self.encoder = None
        self.ml_model = None
        self.tracker = None
        self.trained_model = None
        self.validation_metrics = None
        logger.info("ProblemBase inicializado com sucesso.")

    def stream_processed(self):
        """
        Gera um fluxo de dados processados, garantindo que todas as chaves obrigatórias existam.
        """
        logger.info("Gerando fluxo de dados processados.")
        required_keys = ['Cultura', 'Área colhida (ha)', 'Valor da Produção Total', 'Rendimento médio (kg/ha)']

        def ensure_keys(row):
            for key in required_keys:
                if key not in row:
                    logger.warning(f"Chave ausente '{key}' detectada. Adicionando valor padrão.")
                    row[key] = 0.0 if key != 'Cultura' else 'Indefinido'
            return row

        return (ensure_keys(row) for row in self._stream_data(self.problem_name))

    def stream_features(self):
        """
        Gera um fluxo de features processadas.
        """
        logger.info("Gerando fluxo de features processadas.")
        for processed_row in self.stream_processed():
            yield self.feature_set.features(processed_row)
        logger.info("Fluxo de features processadas gerado com sucesso.")

    def get_encoder(self, write=False, read_from_file=False):
        """
        Cria ou recupera o encoder treinado para os dados.
        """
        logger.info("Criando ou recuperando o encoder.")
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
        logger.info("Encoder inicializado. Adicionando estatísticas numéricas.")
        try:
            self.encoder.add_numeric_stats(self.stream_features())
        except KeyError as e:
            logger.error(f"Erro ao adicionar estatísticas numéricas ao encoder: {e}")
            raise

        runtime = time() - start
        logger.info(f"Configuração do encoder concluída em {runtime:.2f} segundos.")

    def training_stream(self):
        """
        Gera o fluxo de dados de treinamento.
        """
        logger.info("Gerando fluxo de treinamento.")
        return (row for row in self.stream_processed() if self.training_filter(row))

    def validation_stream(self):
        """
        Gera o fluxo de dados de validação.
        """
        logger.info("Gerando fluxo de validação.")
        filtered_data = [row for row in self.stream_processed() if self.validation_filter(row)]
        logger.info(f"Fluxo de validação contém {len(filtered_data)} linhas.")
        if not filtered_data:
            logger.error("Fluxo de validação está vazio. Verifique os filtros ou os dados de entrada.")
            raise ValueError("Fluxo de validação vazio.")
        return iter(filtered_data)

    def train(self):
        """
        Realiza o treinamento do modelo.
        """
        if self.ml_model:
            logger.warning("Modelo já treinado. Treinamento adicional não permitido.")
            return

        logger.info("Iniciando treinamento do modelo.")
        start = time()

        if not self.encoder:
            self.get_encoder()

        self.ml_model = MLModel(self.specification.spec['algorithm_name_actual'],
                                self.algorithm_params,
                                self.feature_set,
                                self.encoder,
                                self.ml_pipeline_params['training_random_seed'])

        self.ml_model.train(self.training_stream())
        self.trained_model = self.ml_model.trained_model
        self.importance = get_feature_importance(self.trained_model,
                                                 self.specification.spec['algorithm_name_actual'],
                                                 self.encoder)

        runtime = time() - start
        logger.info(f"Treinamento do modelo concluído em {runtime:.2f} segundos.")

    def validate(self):
        """
        Realiza a validação do modelo.
        """
        logger.info("Iniciando validação do modelo.")
        start = time()

        true_validation_target = list(self.true_target_stream(self.validation_stream()))
        validation_prediction = list(self.ml_model.predict_processed_rows(self.validation_stream()))

        if not true_validation_target:
            logger.error("Conjunto de validação vazio. Não é possível calcular métricas.")
            raise ValueError("Conjunto de validação vazio.")

        validation_metric_names = self.ml_pipeline_params['validation_metric_names']
        self.validation_metrics = get_validation_metrics(validation_metric_names,
                                                         true_validation_target,
                                                         validation_prediction,
                                                         None,  # Não usado em regressão
                                                         None)

        runtime = time() - start
        logger.info(f"Validação do modelo concluída em {runtime:.2f} segundos.")

    def make_specification(self):
        return Specification(self.problem_name,
                             self.data_downloader,
                             self.ml_pipeline_params_name,
                             self.feature_set_name,
                             self.algorithm_name,
                             self.algorithm_params_name,
                             self.resolved_algorithm_name)

    def get_ml_pipeline_params(self, ml_pipeline_params_name):
        path = Path(__file__).parent / self.problem_name / 'ml_pipelines' / f"{ml_pipeline_params_name}.json"
        logger.info(f"Carregando parâmetros do pipeline de ML de {path}.")
        return self.read_json_file(path)

    def get_algorithm_params(self, algorithm_name, algorithm_params_name):
        path = Path(__file__).parent / self.problem_name / 'algorithms' / algorithm_name / f"{algorithm_params_name}.json"
        logger.info(f"Carregando parâmetros do algoritmo de {path}.")
        return self.read_json_file(path)

    def read_json_file(self, path):
        try:
            with open(path, 'r') as file:
                return json.load(file)
        except Exception as e:
            logger.error(f"Erro ao carregar arquivo JSON {path}: {e}")
            raise

    def __repr__(self):
        return '\n'.join([f"{key}: {value}" for key, value in self.__dict__.items() if value is not None])