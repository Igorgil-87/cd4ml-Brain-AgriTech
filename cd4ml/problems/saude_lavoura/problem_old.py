from cd4ml.problems.problem_base import ProblemBase

class SaudeLavouraProblem(ProblemBase):
    def __init__(self, problem_name, data_downloader='default', ml_pipeline_params_name='default',
                 feature_set_name='default', algorithm_name='default', algorithm_params_name='default'):
        super(SaudeLavouraProblem, self).__init__(problem_name,
                                                  data_downloader=data_downloader,
                                                  ml_pipeline_params_name=ml_pipeline_params_name,
                                                  feature_set_name=feature_set_name,
                                                  algorithm_name=algorithm_name,
                                                  algorithm_params_name=algorithm_params_name)

    @staticmethod
    def get_feature_set_constructor(feature_set_name):
        if feature_set_name == 'default':
            from cd4ml.problems.saude_lavoura.features.feature_sets.default.feature_set import SaudeLavouraFeatureSet
            return SaudeLavouraFeatureSet
        else:
            raise ValueError(f"Feature set {feature_set_name} not recognized")
