import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
from dagster import op
import mlflow.sklearn

from cd4ml_pipeline.shared.mlflow_utils import init_mlflow, assess_model_performance

@op
def train_insumo():
    # Inicializa o MLflow e define o experimento
    init_mlflow(experiment_name="insumo")

    # Leitura do dataset
    df = pd.read_csv("data/insumo.csv")
    df = df.dropna()

    # Features e variável alvo
    X = df[['ano', 'mes']]
    y = df['media_estadual']

    # Split do dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Modelo de Regressão Ridge
    model = Ridge()
    model.fit(X_train, y_train)

    # Log no MLflow
    with mlflow.start_run():
        mlflow.sklearn.log_model(model, "model")
        assess_model_performance(model, X_test, y_test)