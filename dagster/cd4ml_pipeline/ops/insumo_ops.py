from dagster import op
from cd4ml_pipeline.shared.mlflow_utils import init_mlflow

@op
def train_insumo():
    mlflow = init_mlflow()
    with mlflow.start_run(run_name="treino_insumo"):
        mlflow.log_param("modelo", "linear")
        mlflow.log_metric("erro", 0.33)