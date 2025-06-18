from dagster import op
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import mlflow

from cd4ml_pipeline.shared.mlflow_utils import start_run, assess_model_performance

@op
def preprocess_rendimento() -> pd.DataFrame:
    np.random.seed(42)
    df = pd.DataFrame({
        "ano": np.random.randint(2010, 2023, 100),
        "mes": np.random.randint(1, 13, 100),
        "uf": np.random.choice(["SP", "MG", "PR"], 100),
        "mediaEst": np.random.rand(100) * 100,
        "mediaNac": np.random.rand(100) * 100,
        "produtividade": np.random.rand(100) * 50
    })
    return df

@op
def train_rendimento_model(df: pd.DataFrame) -> float:
    X = df[["ano", "mes", "mediaEst", "mediaNac"]]
    y = df["produtividade"]

    model = LinearRegression()
    model.fit(X, y)

    with start_run("rendimento_model") as run:
        mlflow.log_param("model_type", "LinearRegression")

        assess_model_performance(model, X, y)  # logs rmse e r2

        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name="rendimento"
        )

    return float(mean_squared_error(y, model.predict(X), squared=False))