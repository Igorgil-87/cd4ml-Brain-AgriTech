class CommoditiesFeatureSet:
    base_field_schema = {
        "region": "string",
        "commodity": "string",
        "season": "string",
        "area": "float",
        "production": "float",
        "price": "float",
        "yield": "float"
    }

    identifier_field = "region"
    target_field = "price"

    derived_field_schema = {
        "yield_per_area": lambda row: row["production"] / row["area"] if row["area"] > 0 else 0
    }

    def __init__(self, identifier_field, target_field, info):
        self.identifier_field = identifier_field
        self.target_field = target_field
        self.info = info

    @staticmethod
    def features(row):
        # Lógica para transformar os dados (caso necessário)
        # Exemplo: Adicionando campos derivados aos dados
        row["yield_per_area"] = row["production"] / row["area"] if row["area"] > 0 else 0
        return row


# Adicionando a função `get_feature_set`
def get_feature_set(identifier_field, target_field, params):
    """
    Função para instanciar o CommoditiesFeatureSet.

    :param identifier_field: Campo identificador
    :param target_field: Campo alvo (target)
    :param params: Parâmetros adicionais
    :return: Instância do CommoditiesFeatureSet
    """
    return CommoditiesFeatureSet(identifier_field, target_field, params)
