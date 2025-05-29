from dagster import asset
import pandas as pd
import numpy as np

@asset
def saude_lavoura_data() -> pd.DataFrame:
    np.random.seed(3)
    data = pd.DataFrame({
        "ano": np.random.choice([2021, 2022, 2023], size=100),
        "mes": np.random.randint(1, 13, size=100),
        "uf": np.random.choice(["SP", "PR", "MG", "MT"], size=100),
        "cultura": np.random.choice(["Soja", "Milho", "Café"], size=100),
        "indicador_umidade": np.random.uniform(40.0, 80.0, size=100),
        "pragas_detectadas": np.random.randint(0, 5, size=100),
        "risco_doenca": np.round(np.random.uniform(0.0, 1.0, size=100), 2)
    })
    return data