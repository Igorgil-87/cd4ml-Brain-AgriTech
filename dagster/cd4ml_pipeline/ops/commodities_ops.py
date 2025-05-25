from dagster import op
from cd4ml_pipeline.ops.shared.mlflow_utils import init_mlflow
from cd4ml_pipeline.ops.shared.pre_process import preprocess_data
from cd4ml_pipeline.ops.shared.validate import validate_schema

@op
def train_commodities():
    print("📦 Preparando dados de commodities...")
    preprocess_data("commodities")
    validate_schema("commodities")

    mlflow = init_mlflow()
    with mlflow.start_run(run_name="treino_commodities"):
        mlflow.log_param("modelo", "LSTM")
        mlflow.log_metric("rmse", 0.15)