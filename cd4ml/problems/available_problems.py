import cd4ml.problems.groceries.problem as groceries_scenario
import cd4ml.problems.houses.problem as houses_scenario
import cd4ml.problems.iris.problem as iris_scenario
#import cd4ml.problems.agro.colheita.problem as colheita_scenario
from cd4ml.problems.commodities.problem import CommoditiesProblem
from cd4ml.problems.saude_lavoura.problem import SaudeLavouraProblem


from cd4ml.problems.insumo.problem import InsumoProblem
from cd4ml.problems.rendimento.problem import RendimentoProblem
from cd4ml.problems.saude_lavoura.problem import SaudeLavouraProblem
from cd4ml.problems.insumo.problem import InsumoProblem

    





PROBLEMS = {
    'groceries': groceries_scenario.Problem,
    'houses': houses_scenario.Problem,
    'iris': iris_scenario.Problem,
    "commodities": CommoditiesProblem(
        problem_name="commodities",
        data_downloader="default",
        ml_pipeline_params_name="default",
        feature_set_name="default",
        algorithm_name="default",
        algorithm_params_name="default"
    ),
    "saude_lavoura": SaudeLavouraProblem(
        problem_name="saude_lavoura",
        data_downloader="default",
        ml_pipeline_params_name="default",
        feature_set_name="default",
        algorithm_name="random_forest",
        algorithm_params_name="default"
        ),
    # Outros problemas...
    "insumo": InsumoProblem(problem_name="insumo"),
    "rendimento": RendimentoProblem(
        problem_name="rendimento",
        data_downloader="default",
        ml_pipeline_params_name="default",
        feature_set_name="default",
        algorithm_name="random_forest",
        algorithm_params_name="default"
        )

}
