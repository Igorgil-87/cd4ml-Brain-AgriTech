import cd4ml.problems.insumo.problem as insumo_scenario
import cd4ml.problems.rendimento.problem as rendimento_scenario
import cd4ml.problems.saude_lavoura.problem as saude_lavoura_scenario
from cd4ml.problems.commodities.problem import CommoditiesProblem

# Dicionário de problemas atualizados
PROBLEMS = {
    "insumo": insumo_scenario.Problem(
        problem_name="insumo",
        data_downloader="default",
        ml_pipeline_params_name="default",
        feature_set_name="default",
        algorithm_name="default",
        algorithm_params_name="default"
    ),
    "rendimento": rendimento_scenario.Problem(
        problem_name="rendimento",
        data_downloader="default",
        ml_pipeline_params_name="default",
        feature_set_name="default",
        algorithm_name="random_forest",
        algorithm_params_name="default"
    ),
    "saude_lavoura": saude_lavoura_scenario.Problem(
        problem_name="saude_lavoura",
        data_downloader="default",
        ml_pipeline_params_name="default",
        feature_set_name="default",
        algorithm_name="random_forest",
        algorithm_params_name="default"
    ),
    "commodities": CommoditiesProblem(
        problem_name="commodities",
        data_downloader="default",
        ml_pipeline_params_name="default",
        feature_set_name="default",
        algorithm_name="default",
        algorithm_params_name="default"
    )
}