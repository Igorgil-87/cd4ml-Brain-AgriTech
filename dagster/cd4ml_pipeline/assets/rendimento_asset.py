from dagster import asset
import pandas as pd
import numpy as np

@asset
def rendimento_data() -> pd.DataFrame:
    # Simulando um dataset
    np.random.seed(42)
    data = pd.DataFrame({
        "ano": np.random.choice([2020, 2021, 2022, 2023], size=100),
        "uf": np.random.choice(["SP", "PR", "RS", "MT"], size=100),
        "cultura": np.random.choice(["Soja", "Milho"], size=100),
        "media_estadual": np.random.uniform(2.0, 5.0, size=100),
        "media_nacional": np.random.uniform(2.5, 5.5, size=100),
        "unidade": "tonelada"
    })
    return data