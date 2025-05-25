from dagster import op
import os
import mlflow

@op
def treina_modelo():
    os.environ["MLFLOW_TRACKING_URI"] = "http://mlflow:5000"
    os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://minio:9000"

    with mlflow.start_run(run_name="treino_modelo_dagster"):
        mlflow.log_param("modelo", "random_forest")
        mlflow.log_metric("rmse", 0.123)