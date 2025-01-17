import pandas as pd
from cd4ml.feature_set import FeatureSetBase
from cd4ml.utils.feature_utils import get_feature_params, get_generic_feature_set
import logging

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
        Gera características derivadas categóricas de maneira robusta.
        """

        # Verificar o tipo de entrada
        self.logger.info(f"Tipo de entrada: {type(base_features)}")
        if isinstance(base_features, dict):
            # Para dicionário, tratar cada valor individualmente
            features = {
                'is_high_value': 1 if float(base_features.get('Valor da Produção Total', 0.0)) > 5000000 else 0,
                'is_milho': 1 if base_features.get('cultura', '') == 'Milho' else 0,
                'is_soja': 1 if base_features.get('cultura', '') == 'Soja' else 0,
            }
        elif isinstance(base_features, pd.Series):
            # Para uma única linha (pd.Series)
            features = {
                'is_high_value': 1 if base_features.get('Valor da Produção Total', 0.0) > 5000000 else 0,
                'is_milho': 1 if base_features.get('cultura', '') == 'Milho' else 0,
                'is_soja': 1 if base_features.get('cultura', '') == 'Soja' else 0,
            }
        elif isinstance(base_features, pd.DataFrame):
            # Para DataFrame, aplicar operações vetorizadas
            features = pd.DataFrame({
                'is_high_value': (base_features['Valor da Produção Total'].astype(float) > 5000000).astype(int),
                'is_milho': (base_features['cultura'] == 'Milho').astype(int),
                'is_soja': (base_features['cultura'] == 'Soja').astype(int),
            })
        else:
            raise ValueError("Formato de entrada inesperado para base_features. Esperado dict, pandas.Series ou pandas.DataFrame.")

        # Retornar as features processadas
        if isinstance(features, dict):
            return {k: features[k] for k in self.params['derived_categorical_n_levels_dict'].keys()}
        elif isinstance(features, pd.DataFrame):
            return features[list(self.params['derived_categorical_n_levels_dict'].keys())]


 

    def derived_features_numerical(self, base_features):
        """
        Gera características derivadas numéricas.
        """
        print(f"Tipo de entrada: {type(base_features)}")
        # Exemplo de derivação de features numéricas
        features = {
            'valor_por_area': base_features.get('valor_producao_total', 0.0) / (base_features.get('area_colhida_ha', 1) + 1),
            'quantidade_por_area': base_features.get('Quantidade produzida (t)', 0.0) / (base_features.get('area_colhida_ha', 1) + 1),
            'rendimento_normalizado': base_features.get('Rendimento médio (kg/ha)', 0.0) / 1000.0  # Normalização simples
        }
        return {k: features[k] for k in self.params['derived_fields_numerical']}

    def base_features(self, processed_row):
        """
        Retorna as features base, garantindo valores padrão para campos ausentes.
        """
        features = {
            'uf': processed_row.get('UF', 'N/A'),  # Deve ser 'UF' (uppercase) se assim estiver nos dados.
            'municipio': processed_row.get('Município', 'N/A'),
            'solo': processed_row.get('Solo', 'Desconhecido'),
            'cultura': processed_row.get('Cultura', 'Indefinida'),
            'safra': processed_row.get('Safra', '0000/0000'),
            'grupo': processed_row.get('Grupo', 'Grupo Desconhecido'),
            'decenio': processed_row.get('Decênio', '01/01-10/01'),
            'area_colhida_ha': processed_row.get('Área colhida (ha)', 100),
            'valor_producao_total': processed_row.get('Valor da Produção Total', 0.0),
            'Quantidade produzida (t)': processed_row.get('Quantidade produzida (t)', 0.0),
            'Rendimento médio (kg/ha)': processed_row.get('Rendimento médio (kg/ha)', 0.0)
        }
        return features