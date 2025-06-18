from dagster import op
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from cd4ml_pipeline.shared.mlflow_utils import start_run, assess_model_performance
import mlflow

@op
def train_saude_lavoura(df: pd.DataFrame):
    df = df.dropna()

    X = df[['ano', 'mes', 'indicador_umidade', 'pragas_detectadas']]
    y = df['risco_doenca']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(random_state=42)
    model.fit(X_train, y_train)

    with start_run("saude_lavoura") as run:
        mlflow.log_param("model_type", "RandomForestRegressor")
        assess_model_performance(model, X_test, y_test)
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name="saude_lavoura"
        )