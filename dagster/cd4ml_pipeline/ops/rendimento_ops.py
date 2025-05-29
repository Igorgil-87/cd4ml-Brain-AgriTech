import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import joblib
from dagster import op
from cd4ml_pipeline.ops.shared.mlflow_utils import start_run

@op
def train_rendimento_model():
    # Simulação de dados temporários
    np.random.seed(42)
    df = pd.DataFrame({
        "ano": np.random.randint(2010, 2023, 100),
        "mes": np.random.randint(1, 13, 100),
        "uf": np.random.choice(["SP", "MG", "PR"], 100),
        "mediaEst": np.random.rand(100) * 100,
        "mediaNac": np.random.rand(100) * 100,
        "produtividade": np.random.rand(100) * 50
    })

    X = df[["ano", "mes", "mediaEst", "mediaNac"]]
    y = df["produtividade"]

    model = LinearRegression()
    model.fit(X, y)
    predictions = model.predict(X)
    rmse = np.sqrt(mean_squared_error(y, predictions))

    with start_run("rendimento_model") as run:
        mlflow.log_param("model_type", "LinearRegression")
        mlflow.log_metric("rmse", rmse)
        model_path = "model_rendimento.pkl"
        joblib.dump(model, model_path)
        mlflow.log_artifact(model_path)

    return rmse