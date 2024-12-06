from cd4ml.problems.problem_base import ProblemBase
from cd4ml.problems.rendimento.readers.stream_data import stream_data
from cd4ml.problems.rendimento.features.feature_sets.default.feature_set import get_feature_set


class RendimentoProblem(ProblemBase):
    def __init__(self,
                 problem_name,
                 data_downloader='default',
                 ml_pipeline_params_name='default',
                 feature_set_name='default',
                 algorithm_name='default',
                 algorithm_params_name='default'):

        super(RendimentoProblem, self).__init__(problem_name,
                                                data_downloader=data_downloader,
                                                feature_set_name=feature_set_name,
                                                ml_pipeline_params_name=ml_pipeline_params_name,
                                                algorithm_name=algorithm_name,
                                                algorithm_params_name=algorithm_params_name)
        self._stream_data = stream_data

    @staticmethod
    def get_feature_set_constructor(feature_set_name):
        if feature_set_name == 'default':
            return get_feature_set
        else:
            raise ValueError(f"Feature set name {feature_set_name} is not valid for RendimentoProblem.")

    def prepare_feature_data(self):
        # Implementação de lógica para transformação de dados específicos de rendimento.
        pass

    def download_data(self):
        # Aqui você implementa o download dos dados, se necessário.
        pass
