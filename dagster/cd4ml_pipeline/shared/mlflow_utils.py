import mlflow
import mlflow.sklearn
import os
from dagster import get_dagster_logger
from sklearn.metrics import mean_squared_error, r2_score

logger = get_dagster_logger()

def init_mlflow():
    """Inicializa variáveis de ambiente e URI do MLflow."""
    os.environ.setdefault("MLFLOW_TRACKING_URI", "http://mlflow:5000")
    os.environ.setdefault("MLFLOW_S3_ENDPOINT_URL", "http://minio:9000")
    logger.info(f"MLflow Tracking URI: {os.environ['MLFLOW_TRACKING_URI']}")
    logger.info(f"MLflow S3 Endpoint: {os.environ['MLFLOW_S3_ENDPOINT_URL']}")
    mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])

def start_run(name: str):
    """Inicia um experimento nomeado no MLflow."""
    init_mlflow()
    mlflow.set_experiment(name)
    return mlflow.start_run(run_name=name)

def log_model_to_mlflow(model, model_name: str, metrics: dict = None, params: dict = None):
    """Registra modelo no MLflow com métricas e parâmetros opcionais."""
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
        logger.info(f"Model '{model_name}' logged to MLflow with metrics: {metrics}")

def assess_model_performance(model, X_test, y_test):
    """Calcula métricas RMSE e R2, e registra no MLflow."""
    predictions = model.predict(X_test)
    rmse = mean_squared_error(y_test, predictions, squared=False)
    r2 = r2_score(y_test, predictions)
    mlflow.log_metric("rmse", rmse)
    mlflow.log_metric("r2_score", r2)
    logger.info(f"Model evaluation - RMSE: {rmse}, R²: {r2}")