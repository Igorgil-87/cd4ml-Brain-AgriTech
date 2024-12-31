from cd4ml.problems.problem_base import ProblemBase
import cd4ml.problems.rendimento.readers.stream_data as data_streamer
import cd4ml.problems.rendimento.download_data.download_data as dd
import logging

class Problem(ProblemBase):
    def __init__(self,
                 problem_name,
                 data_downloader='default',
                 ml_pipeline_params_name='default',
                 feature_set_name='default',
                 algorithm_name='default',
                 algorithm_params_name='default'):

        # Chama a inicialização da classe base
        super(Problem, self).__init__(problem_name,
                                      data_downloader=data_downloader,
                                      feature_set_name=feature_set_name,
                                      ml_pipeline_params_name=ml_pipeline_params_name,
                                      algorithm_name=algorithm_name,
                                      algorithm_params_name=algorithm_params_name)

        self.logger = logging.getLogger(__name__)
        self._stream_data = data_streamer.stream_data  # Stream de dados específico

        # Define filtros de treino e validação
        self.training_filter, self.validation_filter = data_streamer.get_training_validation_filters(self.ml_pipeline_params)

    @staticmethod
    def get_feature_set_constructor(feature_set_name):
        """
        Retorna o construtor do feature set.
        """
        if feature_set_name == "default":
            from cd4ml.problems.rendimento.features.feature_sets.default import feature_set as fs
            return fs.get_feature_set
        else:
            raise ValueError(f"Feature set '{feature_set_name}' não é válido para o problema 'rendimento'.")

    def download_data(self):
        """
        Executa o download dos dados do problema.
        """
        self.logger.info("Iniciando download de dados...")
        dd.download(self.problem_name)  # Passa o problem_name para download
        self.logger.info("Download concluído.")