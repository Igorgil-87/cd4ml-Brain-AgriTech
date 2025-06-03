# cd4ml_pipeline/ops/saude_lavoura_ops.py

from dagster import op
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import mlflow
import mlflow.sklearn

from cd4ml_pipeline.shared.mlflow_utils import init_mlflow, assess_model_performance

@op
def train_saude_lavoura(df: pd.DataFrame):
    # Inicializa MLflow e define o experimento
    init_mlflow()
    mlflow.set_experiment("saude_lavoura")

    # Pré-processamento
    df = df.dropna()
    
    # Features e alvo
    X = df[['ano', 'mes', 'indicador_umidade', 'pragas_detectadas']]
    y = df['risco_doenca']

    # Split dos dados
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Treinamento do modelo
    model = RandomForestRegressor(random_state=42)
    model.fit(X_train, y_train)

    # Logging no MLflow
    with mlflow.start_run():
        mlflow.sklearn.log_model(model, "model")
        assess_model_performance(model, X_test, y_test)