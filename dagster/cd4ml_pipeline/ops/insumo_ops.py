# cd4ml_pipeline/ops/insumo_ops.py

from dagster import op
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
import mlflow.sklearn

from cd4ml_pipeline.shared.mlflow_utils import init_mlflow, assess_model_performance

@op
def train_insumo(context, insumo_data: pd.DataFrame):
    init_mlflow()  # inicializa MLflow
    mlflow.set_experiment("insumo")  # define o experimento
    context.log.info(f"Colunas disponíveis: {insumo_data.columns.tolist()}")

    df = insumo_data.dropna()

    X = df[['ano', 'mes']]
    y = df['media_estadual']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = Ridge()
    model.fit(X_train, y_train)

    with mlflow.start_run():
        mlflow.sklearn.log_model(model, "model")
        assess_model_performance(model, X_test, y_test)