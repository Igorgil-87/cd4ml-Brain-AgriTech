class InsumoFeatureSet:
    base_field_schema = {
        "region": "string",
        "insumo_type": "string",  # Tipo de insumo (fertilizante, defensivo, etc.)
        "quantity": "float",     # Quantidade de insumo utilizada
        "cost": "float",         # Custo do insumo
        "yield_increase": "float" # Aumento projetado na produção
    }

    identifier_field = "region"
    target_field = "yield_increase"

    derived_field_schema = {
        "cost_per_unit": lambda row: row["cost"] / row["quantity"] if row.get("quantity", 0) > 0 else 0
    }

    def __init__(self, identifier_field, target_field, info):
        self.identifier_field = identifier_field
        self.target_field = target_field
        self.info = info

    @staticmethod
    def features(row):
        """
        Transforma os dados de entrada no formato necessário para o modelo.
        """
        try:
            features = {
                "area": float(row["area"]),
                "cultura": int(row["cultura"]),  # Presumindo que 'cultura' é um mapeamento numérico
                "date": row["date"]  # Assumindo que 'date' é uma string
            }
            
            # Gerar campos derivados
            if "cost" in row and "quantity" in row:
                features["cost_per_unit"] = row["cost"] / row["quantity"] if row["quantity"] > 0 else 0
            else:
                features["cost_per_unit"] = 0

            return features
        except KeyError as e:
            raise ValueError(f"Faltando campo obrigatório no dado de entrada: {e}")
        except Exception as e:
            raise ValueError(f"Erro ao processar os dados: {e}")

    def ml_fields(self):
        """
        Retorna os campos obrigatórios para previsão.
        """
        return ["area", "cultura", "date"]

def get_feature_set(identifier_field=None, target_field=None, info=None):
    """
    Retorna uma instância de `InsumoFeatureSet` com os campos especificados.
    """
    return InsumoFeatureSet(identifier_field, target_field, info)
