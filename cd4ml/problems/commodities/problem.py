from cd4ml.problems.problem_base import ProblemBase
from cd4ml.problems.commodities.download_data.download_data import download  # Altere para usar a nova função padrão
import cd4ml.problems.commodities.readers.stream_data as stream_data
from cd4ml.utils.utils import average_by

class CommoditiesProblem(ProblemBase):
    def __init__(self,
                 problem_name="commodities",
                 data_downloader="default",
                 ml_pipeline_params_name="default",
                 feature_set_name="default",
                 algorithm_name="default",
                 algorithm_params_name="default"):
        super(CommoditiesProblem, self).__init__(problem_name,
                                                 data_downloader=data_downloader,
                                                 feature_set_name=feature_set_name,
                                                 ml_pipeline_params_name=ml_pipeline_params_name,
                                                 algorithm_name=algorithm_name,
                                                 algorithm_params_name=algorithm_params_name)

        self._stream_data = stream_data.stream_data

    @staticmethod
    def get_feature_set_constructor(feature_set_name):
        if feature_set_name == 'default':
            from cd4ml.problems.commodities.features.feature_sets.default.feature_set import get_feature_set
            return get_feature_set
        else:
            raise ValueError(f"Feature set name {feature_set_name} is not valid for CommoditiesProblem.")

    def prepare_feature_data(self):
        """
        Prepara os dados de características específicas para o problema de commodities.
        """
        train_data = self.training_stream()
        avg_price_prior = 100.0  # Preço médio usado como base para suavização
        prior_num = 5  # Número de exemplos fictícios para suavização

        # Calcula as médias por região
        averages = average_by(train_data, "price", "region",
                              prior_num=prior_num,
                              prior_value=avg_price_prior)

        # Atualiza as informações do conjunto de características
        for region in self.feature_set.info.get("regions", {}).keys():
            region_avg = averages.get(region, (avg_price_prior, 0))
            self.feature_set.info["regions"][region]["avg_price"] = region_avg[0]
            self.feature_set.info["regions"][region]["num_sales"] = region_avg[1]

    def download_data(self):
        """
        Faz o download dos dados para o problema de commodities.
        """
        download()  # Chama a nova função `download` padrão