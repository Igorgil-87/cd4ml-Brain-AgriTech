from dagster import op
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from cd4ml_pipeline.shared.mlflow_utils import start_run, assess_model_performance
import mlflow

@op
def train_commodities(df: pd.DataFrame):
    df = df.dropna()

    X = df[['ano', 'mes']]
    y = df['media_nacional']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LinearRegression()
    model.fit(X_train, y_train)

    with start_run("commodities") as run:
        mlflow.log_param("model_type", "LinearRegression")
        assess_model_performance(model, X_test, y_test)
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name="commodities"
        )