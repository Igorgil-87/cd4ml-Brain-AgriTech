import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from dagster import op
from cd4ml_pipeline.shared.mlflow_utils import init_mlflow, assess_model_performance
import mlflow.sklearn


@op
def train_commodities():
    init_mlflow()
    mlflow.set_experiment("commodities")

    # Leitura dos dados
    df = pd.read_csv("data/commodities.csv")
    df = df.dropna()

    # Features e target
    X = df[['ano', 'mes']]
    y = df['media_nacional']

    # Separação treino/teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Modelo
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Log no MLflow
    with mlflow.start_run():
        mlflow.sklearn.log_model(model, "model")
        assess_model_performance(model, X_test, y_test)