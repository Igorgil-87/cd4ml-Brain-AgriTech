from dagster import asset
import pandas as pd
import numpy as np

@asset
def insumo_data() -> pd.DataFrame:
    np.random.seed(2)
    data = pd.DataFrame({
        "ano": np.random.choice([2021, 2022, 2023], size=100),
        "mes": np.random.randint(1, 13, size=100),
        "uf": np.random.choice(["SP", "PR", "MG", "MT"], size=100),
        "cultura": np.random.choice(["Soja", "Milho", "Café"], size=100),
        "tipo_insumo": np.random.choice(["Fertilizante", "Semente", "Defensivo"], size=100),
        "media_estadual": np.random.uniform(200.0, 800.0, size=100),
        "unidade": "R$/ha"
    })
    return data