import cd4ml.problems.insumo.problem as insumo_scenario
import cd4ml.problems.rendimento.problem as rendimento_scenario
import cd4ml.problems.saude_lavoura.problem as saude_lavoura_scenario
from cd4ml.problems.commodities.problem import CommoditiesProblem

# Dicionário de problemas com referências às classes
PROBLEMS = {
    "insumo": insumo_scenario,  # Referência à classe
    "rendimento": rendimento_scenario,  # Referência à classe
    "saude_lavoura": saude_lavoura_scenario,  # Referência à classe
    "commodities": CommoditiesProblem  # Referência à classe
}