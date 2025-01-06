from cd4ml.feature_set import FeatureSetBase
from cd4ml.utils.feature_utils import get_feature_params, get_generic_feature_set

def get_feature_set_params():
    """Carrega os parâmetros do conjunto de features a partir do JSON."""
    return get_feature_params(__file__)

def get_feature_set(identifier_field, target_field, info):
    """Retorna o conjunto de features genérico configurado."""
    return get_generic_feature_set(identifier_field, target_field, info, __file__, FeatureSet)

class FeatureSet(FeatureSetBase):
    def __init__(self, identifier_field, target_field, info, feature_set_params):
        super(FeatureSet, self).__init__(identifier_field, target_field)
        self.info = info
        self.params = feature_set_params

    def derived_features_categorical(self, base_features):
        """
        Gera características derivadas categóricas.
        """
        features = {
            'is_high_value': 1 if base_features['Valor da Produção Total'] > 5000000 else 0,  # Exemplo: Marcador de alto valor
            'is_milho': 1 if base_features['Cultura'] == 'Milho' else 0,
            'is_soja': 1 if base_features['Cultura'] == 'Soja' else 0
        }
        return {k: features[k] for k in self.params['derived_categorical_n_levels_dict'].keys()}

    def derived_features_numerical(self, base_features):
        """
        Gera características derivadas numéricas.
        """
        # Exemplo de derivação de features numéricas
        features = {
            'valor_por_area': base_features['Valor da Produção Total'] / (base_features['Área colhida (ha)'] + 1),  # Evita divisão por zero
            'quantidade_por_area': base_features['Quantidade produzida (t)'] / (base_features['Área colhida (ha)'] + 1),
            'rendimento_normalizado': base_features['Rendimento médio (kg/ha)'] / 1000.0  # Normalização simples
        }
        return {k: features[k] for k in self.params['derived_fields_numerical']}

    def base_features(self, processed_row):
        """
        Retorna as features base.
        """
        features = {
            'uf': processed_row['uf'],
            'municipio': processed_row['municipio'],
            'solo': processed_row['solo'],
            'cultura': processed_row['cultura'],
            'safra': processed_row['safra'],
            'grupo': processed_row['grupo'],
            'decenio': processed_row['decenio'],
            'area_colhida_ha': processed_row['Área colhida (ha)'],
            'valor_producao_total': processed_row['Valor da Produção Total']
        }
        return features