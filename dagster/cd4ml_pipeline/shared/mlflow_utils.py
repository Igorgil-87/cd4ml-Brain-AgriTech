import os
import mlflow

def init_mlflow():
    os.environ["MLFLOW_TRACKING_URI"] = "http://mlflow:5000"
    os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://minio:9000"
    return mlflow