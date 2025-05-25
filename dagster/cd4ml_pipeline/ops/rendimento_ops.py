from dagster import op
import mlflow
import os

@op
def train_rendimento_model():
    os.environ["MLFLOW_TRACKING_URI"] = "http://mlflow:5000"
    os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://minio:9000"

    # simula seu script `cd4ml/problems/rendimento/...`
    print("Treinando modelo de rendimento...")
    with mlflow.start_run(run_name="rendimento_treino"):
        mlflow.log_param("modelo", "xgboost")
        mlflow.log_metric("mae", 0.12)