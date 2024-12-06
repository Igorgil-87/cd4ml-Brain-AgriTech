class SaudeLavouraFeatureSet:
    base_field_schema = {
        "region": "string",
        "vegetation_index": "float",
        "soil_moisture": "float",
        "temperature": "float",
        "precipitation": "float"
    }

    identifier_field = "region"
    target_field = "vegetation_index"

    derived_field_schema = {
        "health_score": lambda row: (row["vegetation_index"] + row["soil_moisture"]) / 2
    }

    def __init__(self, identifier_field, target_field, info):
        self.identifier_field = identifier_field
        self.target_field = target_field
        self.info = info

    @staticmethod
    def features(row):
        # Adicione lógica de transformação
        return row
