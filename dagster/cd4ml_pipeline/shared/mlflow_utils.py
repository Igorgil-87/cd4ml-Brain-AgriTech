import mlflow
import mlflow.sklearn
import os
from dagster import get_dagster_logger
from sklearn.metrics import mean_squared_error, r2_score

logger = get_dagster_logger()

def init_mlflow():
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
    s3_endpoint = os.getenv("MLFLOW_S3_ENDPOINT_URL", "http://minio:9000")
    backend_uri = os.getenv("BACKEND_STORE_URI", "postgresql+psycopg2://agro_user:agro_password@postgres:5432/brain_agro")

    logger.info(f"🔗 MLflow Tracking URI: {tracking_uri}")
    logger.info(f"🪣 MLflow S3 Endpoint: {s3_endpoint}")
    logger.info(f"🗃️ MLflow Backend Store URI: {backend_uri}")

    os.environ["MLFLOW_TRACKING_URI"] = tracking_uri
    os.environ["MLFLOW_S3_ENDPOINT_URL"] = s3_endpoint
    os.environ["BACKEND_STORE_URI"] = backend_uri

    mlflow.set_tracking_uri(tracking_uri)

def start_run(name: str):
    """Inicia run seguro e evita duplicidade de tags."""
    init_mlflow()

    # Evita conflito com runs anteriores
    if mlflow.active_run():
        mlflow.end_run()


    mlflow.set_experiment(name)
    return mlflow.start_run()

def log_model_to_mlflow(model, model_name: str, metrics: dict = None, params: dict = None):
    init_mlflow()
    with mlflow.start_run(run_name=model_name):
        if params:
            mlflow.log_params(params)
        if metrics:
            mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name=model_name
        )
        logger.info(f"✅ Model '{model_name}' logged to MLflow.")

def assess_model_performance(model, X_test, y_test):
    predictions = model.predict(X_test)
    rmse = mean_squared_error(y_test, predictions, squared=False)
    r2 = r2_score(y_test, predictions)
    mlflow.log_metric("rmse", rmse)
    mlflow.log_metric("r2_score", r2)
    logger.info(f"📊 Avaliação - RMSE: {rmse}, R²: {r2}")