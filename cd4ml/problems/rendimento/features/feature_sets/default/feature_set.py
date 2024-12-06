class RendimentoFeatureSet:
    base_field_schema = {
        "region": "string",
        "area": "float",
        "season": "string",
        "production": "float",
        "yield": "float",
    }

    identifier_field = "region"
    target_field = "yield"

    derived_field_schema = {
        "production_per_area": lambda row: row["production"] / row["area"] if row["area"] > 0 else 0
    }

    def __init__(self, identifier_field, target_field, info):
        self.identifier_field = identifier_field
        self.target_field = target_field
        self.info = info

    @staticmethod
    def features(row):
        # Adicione lógica de transformação
        return row


def get_feature_set(identifier_field, target_field, info):
    return RendimentoFeatureSet(identifier_field, target_field, info)
