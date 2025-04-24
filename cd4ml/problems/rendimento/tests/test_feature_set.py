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
        "year": "2023"
    }

def test_derived_features_categorical(base_features):
    """Testa a geração de features categóricas derivadas."""
    feature_set = FeatureSet("Cultura", "Rendimento médio (kg/ha)", {}, {})
    categorical_features = feature_set.derived_features_categorical(base_features)
    assert "month" in categorical_features, "Feature 'month' não foi criada corretamente"
    assert categorical_features["month"] == "3", "Falha na conversão de 'month'"

def test_derived_features_numerical(base_features):
    """Testa a geração de features numéricas derivadas."""
    feature_set = FeatureSet("Cultura", "Rendimento médio (kg/ha)", {}, {})
    numerical_features = feature_set.derived_features_numerical(base_features)
    assert "day" in numerical_features, "Feature 'day' não foi criada corretamente"
    assert numerical_features["day"] == 10, "Falha no processamento de 'day'"