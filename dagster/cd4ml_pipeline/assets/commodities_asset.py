from dagster import asset
import pandas as pd
import numpy as np

@asset
def commodities_data() -> pd.DataFrame:
    np.random.seed(1)
    data = pd.DataFrame({
        "ano": np.random.choice([2021, 2022, 2023], size=100),
        "mes": np.random.randint(1, 13, size=100),
        "uf": np.random.choice(["SP", "PR", "MG", "MT"], size=100),
        "cultura": np.random.choice(["Soja", "Milho", "Café"], size=100),
        "media_estadual": np.random.uniform(50, 250, size=100),
        "media_nacional": np.random.uniform(60, 260, size=100),
        "unidade": "saca"
    })
    return data