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
from cd4ml.utils.utils import hash_to_uniform_random
import logging


from cd4ml.download_script import download  # Importa a função download que você já criou



logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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
        logger.info(f"Initializing ProblemBase for problem: {problem_name}")
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

        self.logger.info(f"Model ID created: {self.model_id}")

        if algorithm_name == 'default':
            self.resolved_algorithm_name = self.ml_pipeline_params['default_algorithm']
        else:
            self.resolved_algorithm_name = algorithm_name

        self.specification = self.make_specification()
        self._stream_data = None
        self.training_filter, self.validation_filter = splitter(self.ml_pipeline_params)

        feature_set_class = self.get_feature_set_constructor(feature_set_name)
        self.feature_set = feature_set_class(self.ml_pipeline_params['identifier_field'],
                                             self.ml_pipeline_params['target_field'],
                                             {})
        self.algorithm_params = self.get_algorithm_params(self.resolved_algorithm_name,
                                                          self.algorithm_params_name)

        self.trained_model = None
        self.validation_metrics = None
        self.encoder = None
        self.ml_model = None
        self.tracker = None
        self.feature_data = None
        self.importance = None

    def ensure_keys(self, row, required_keys):
        """
        Garante que todas as chaves obrigatórias estejam presentes no dicionário.
        """
        for key in required_keys:
            if key not in row:
                logger.warning(f"Adicionando chave ausente '{key}' com valor padrão.")
                row[key] = 0.0 if key != 'Cultura' else 'Indefinido'
        return row

    def stream_processed(self):
        """
        Gera um fluxo de dados processados, garantindo que todas as chaves obrigatórias existam.
        """
        logger.info("Gerando fluxo de dados processados.")
        required_keys = ['Cultura', 'Área colhida (ha)', 'Valor da Produção Total', 'Rendimento médio (kg/ha)']

        def ensure_identifier(row):
            # Certifique-se de que 'Cultura' tenha um valor único
            if row['Cultura'] == 'Indefinido':
                row['Cultura'] = f"fallback_{hash(str(row))}"
            return row

        processed_stream = (
            ensure_identifier(self.ensure_keys(row, required_keys))
            for row in self._stream_data(self.problem_name)
        )
        logger.info("Fluxo de dados processados gerado com sucesso.")
        return processed_stream

    def get_encoder(self, write=False, read_from_file=False):
        """
        Cria ou recupera o encoder treinado para os dados.
        """
        logger.info("Criando ou recuperando o encoder.")
        self.prepare_feature_data()
        start = time()

        ml_fields = self.feature_set.ml_fields()
        omitted = self.feature_set.params.get('encoder_untransformed_fields', [])

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
            required_keys = ['Área colhida (ha)', 'Valor da Produção Total', 'Rendimento médio (kg/ha)']
            validated_stream = (self.ensure_keys(row, required_keys) for row in self.stream_features())
            self.encoder.add_numeric_stats(validated_stream)
        except KeyError as e:
            logger.error(f"Erro ao adicionar estatísticas numéricas ao encoder: {e}")
            raise

        runtime = time() - start
        logger.info(f"Configuração do encoder concluída em {runtime:.2f} segundos.")


    def stream_features(self):
        """
        Gera o fluxo de features processadas.
        """
        logger.info("Starting feature stream generation.")
        for processed_row in self.stream_processed():
            yield self.feature_set.features(processed_row)
        logger.info("Feature stream generation completed.")

    def prepare_feature_data(self):
        logger.info("Preparing feature data. This step can be overridden.")
    
    
    def training_stream(self):
        logger.info("Generating training data stream.")
        filtered_data = [row for row in self.stream_processed() if self.training_filter(row)]
        logger.info(f"Training stream contains {len(filtered_data)} rows.")
        return iter(filtered_data)

    def validation_stream(self):
        """
        Gera o fluxo de dados de validação, garantindo que os filtros sejam aplicados corretamente.
        Inclui depuração adicional para verificar a distribuição dos hashes e melhorar o entendimento.
        """
        logger.info("Iniciando geração do fluxo de validação.")
        
        # Contadores para depuração de distribuição de hashes
        hash_counts = {'<0.8': 0, '0.8-1.0': 0}
        
        try:
            # Coleta e processamento de dados
            data = list(self.stream_processed())
            total_rows = len(data)
            logger.info(f"Total de linhas processadas: {total_rows}. Exemplo de dados: {data[:5]}")

            # Aplica o filtro de validação e registra distribuição dos hashes
            filtered_data = []
            for row in data:
                hash_val = hash_to_uniform_random(
                    row[self.feature_set.identifier_field],
                    self.ml_pipeline_params['splitting']['random_seed']
                )
                
                # Depuração da distribuição dos hashes
                if hash_val < 0.8:
                    hash_counts['<0.8'] += 1
                elif 0.8 <= hash_val < 1.0:
                    hash_counts['0.8-1.0'] += 1

                # Filtrar linhas para validação
                if self.validation_filter(row):
                    logger.debug(f"Linha aceita para validação: {row} com hash {hash_val}")
                    filtered_data.append(row)

            # Registra distribuição e resultados
            logger.info(f"Distribuição de hashes: {hash_counts}")
            filtered_rows = len(filtered_data)
            logger.info(f"Linhas após filtro de validação: {filtered_rows} de {total_rows}.")

            # Verifica se há linhas suficientes para validação
            if filtered_rows == 0:
                logger.error("Fluxo de validação vazio. Verifique os dados de entrada ou os filtros.")
                raise ValueError("Validation stream is empty.")

            return iter(filtered_data)
        except Exception as e:
            logger.error(f"Erro ao gerar fluxo de validação: {e}")
            raise



    def train(self):
        """
        Realiza o treinamento do modelo.
        """
        if self.ml_model:
            logger.warning("Model is already trained. Retraining is not allowed.")
            return

        logger.info("Starting model training.")
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
        logger.info(f"Model training completed in {runtime:.2f} seconds.")

    def validate(self):
        """
        Realiza a validação do modelo.
        """
        logger.info("Starting model validation.")
        start = time()

        true_validation_target = list(self.true_target_stream(self.validation_stream()))
        validation_prediction = list(self.ml_model.predict_processed_rows(self.validation_stream()))

        if not true_validation_target:
            logger.error("Validation set is empty. Unable to calculate validation metrics.")
            raise ValueError("Validation set is empty.")

        validation_metric_names = self.ml_pipeline_params['validation_metric_names']
        self.validation_metrics = get_validation_metrics(validation_metric_names,
                                                         true_validation_target,
                                                         validation_prediction,
                                                         None,  # Probabilities not used in regression
                                                         None)

        runtime = time() - start
        logger.info(f"Model validation completed in {runtime:.2f} seconds.")

    def true_target_stream(self, stream):
        return (row[self.feature_set.target_field] for row in stream)

    def run_all(self):
        logger.info("Executando o pipeline completo.")
        try:
            self.setup_tracker()
            self.tracker.log_ml_pipeline_params(self.ml_pipeline_params)

            self.download_data()
            logger.info("Dados baixados com sucesso.")

            self.get_encoder()
            logger.info("Encoder configurado com sucesso.")

            self.train()
            logger.info("Modelo treinado com sucesso.")

            logger.info("Iniciando a validação do modelo.")
            self.validate()

            logger.info("Pipeline completo executado com sucesso.")
        except ValueError as ve:
            logger.error(f"Erro durante a execução do pipeline: {ve}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            raise

    def setup_tracker(self):
        self.tracker = tracking.Track(self.model_id, self.specification.spec)
        logger.info("Tracker setup completed.")

    def download_data(self):
        raise NotImplementedError("This method should be implemented in a subclass.")

    @staticmethod
    def get_feature_set_constructor(feature_set_name):
        raise NotImplementedError("This method should be implemented in a subclass.")

    def get_ml_pipeline_params(self, ml_pipeline_params_name):
        path = Path(Path(__file__).parent, self.problem_name, 'ml_pipelines', f"{ml_pipeline_params_name}.json")
        logger.info(f"Loading ML pipeline parameters from {path}.")
        if not path.exists():
            logger.error(f"Pipeline parameters file {path} does not exist.")
            raise FileNotFoundError(f"Pipeline parameters file {path} not found.")
        return self.read_json_file_for_current_problem_as_dict(path)

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
    

    def make_specification(self):
        return Specification(self.problem_name,
                             self.data_downloader,
                             self.ml_pipeline_params_name,
                             self.feature_set_name,
                             self.algorithm_name,
                             self.algorithm_params_name,
                             self.resolved_algorithm_name)

    def read_json_file_for_current_problem_as_dict(self, file_path):
        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except Exception as e:
            logger.error(f"Error loading JSON file {file_path}: {e}")
            raise

    def __repr__(self):
        return '\n'.join([f"{key}: {value}" for key, value in self.__dict__.items() if value is not None])

class SpecificProblem(ProblemBase):
    """
    Subclasse que implementa o método de download de dados.
    """
    def download_data(self):
        """
        Faz o download dos dados utilizando a função fornecida.
        """
        logger.info("Executando download de dados...")
        self._stream_data = download(problem_name=self.problem_name)
        logger.info("Download de dados concluído com sucesso.")

# Exemplo de uso
if __name__ == "__main__":
    problem = SpecificProblem(
        problem_name="agriculture_analysis",
        data_downloader="custom_downloader",
        ml_pipeline_params_name="default",
        feature_set_name="default",
        algorithm_name="default",
        algorithm_params_name="default"
    )
    problem.run_all()