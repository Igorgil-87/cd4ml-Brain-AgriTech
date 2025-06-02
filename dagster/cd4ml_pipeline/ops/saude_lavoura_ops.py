import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from dagster import op
from cd4ml_pipeline.shared.mlflow_utils import init_mlflow, assess_model_performance
import mlflow.sklearn


@op
def train_saude_lavoura():
    init_mlflow()
    mlflow.set_experiment("saude_lavoura")

    # Leitura dos dados
    df = pd.read_csv("data/saude_lavoura.csv")
    df = df.dropna()

    # Features e target
    X = df[['ano', 'mes']]
    y = df['media_estadual']

    # Separação treino/teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Modelo
    model = RandomForestRegressor()
    model.fit(X_train, y_train)

    # Log no MLflow
    with mlflow.start_run():
        mlflow.sklearn.log_model(model, "model")
        assess_model_performance(model, X_test, y_test)