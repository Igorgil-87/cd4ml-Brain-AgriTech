import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from cd4ml_pipeline.ops.shared.mlflow_utils import init_mlflow, assess_model_performance
import mlflow.sklearn

def train_saude_lavoura():
    init_mlflow(experiment_name="saude_lavoura")

    df = pd.read_csv("data/saude_lavoura.csv")
    df = df.dropna()

    X = df[['ano', 'mes']]
    y = df['media_estadual']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor()
    model.fit(X_train, y_train)

    with mlflow.start_run():
        mlflow.sklearn.log_model(model, "model")
        assess_model_performance(model, X_test, y_test)