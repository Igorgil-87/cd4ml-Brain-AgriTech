# cd4ml_pipeline/ops/commodities_ops.py

from dagster import op
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import mlflow.sklearn

from cd4ml_pipeline.shared.mlflow_utils import init_mlflow, assess_model_performance

@op
def train_commodities(df: pd.DataFrame):
    init_mlflow()
    mlflow.set_experiment("commodities")

    df = df.dropna()

    X = df[['ano', 'mes']]
    y = df['media_nacional']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LinearRegression()
    model.fit(X_train, y_train)

    with mlflow.start_run():
        mlflow.sklearn.log_model(model, "model")
        assess_model_performance(model, X_test, y_test)