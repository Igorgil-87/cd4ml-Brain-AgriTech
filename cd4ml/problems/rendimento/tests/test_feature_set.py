import pytest
from cd4ml.problems.rendimento.features.feature_sets.default.feature_set import FeatureSet
from cd4ml.utils.utils import float_or_zero

@pytest.fixture
def base_features():
    """Fixture para base_features de teste."""
    return {
        "date": "2023-03-10",
        "day": "10",
        "month": "3",
        "year": "2023",
        "cultura": "Milho",
        "Valor da Produção Total": 6000000,
        "valor_producao_total": 70000,
        "area_colhida_ha": 100,
        "Quantidade produzida (t)": 500,
        "Rendimento médio (kg/ha)": 5000
    }

def test_derived_features_categorical(base_features):
    """Testa a geração de features categóricas derivadas."""
    feature_set_params = {'derived_categorical_n_levels_dict': {'is_high_value': 2, 'is_milho': 2, 'is_soja': 2}}
    feature_set = FeatureSet("Cultura", "Rendimento médio (kg/ha)", {}, feature_set_params)
    categorical_features = feature_set.derived_features_categorical(base_features)
    assert "is_high_value" in categorical_features, "Feature 'is_high_value' não foi criada corretamente"
    assert categorical_features["is_high_value"] == 1, "Falha na conversão de 'is_high_value'"
    assert "is_milho" in categorical_features, "Feature 'is_milho' não foi criada corretamente"
    assert categorical_features["is_milho"] == 1, "Falha na conversão de 'is_milho'"

def test_derived_features_numerical(base_features):
    """Testa a geração de features numéricas derivadas."""
    feature_set_params = {'derived_fields_numerical': ['valor_por_area', 'quantidade_por_area', 'rendimento_normalizado']}
    feature_set = FeatureSet("Cultura", "Rendimento médio (kg/ha)", {}, feature_set_params)
    numerical_features = feature_set.derived_features_numerical(base_features)
    assert "valor_por_area" in numerical_features, "Feature 'valor_por_area' não foi criada corretamente"
    assert numerical_features["valor_por_area"] == pytest.approx(693.0693069306931), "Falha no cálculo de 'valor_por_area'"
    assert "rendimento_normalizado" in numerical_features, "Feature 'rendimento_normalizado' não foi criada corretamente"
    assert numerical_features["rendimento_normalizado"] == 5.0, "Falha na normalização de 'rendimento_normalizado'"