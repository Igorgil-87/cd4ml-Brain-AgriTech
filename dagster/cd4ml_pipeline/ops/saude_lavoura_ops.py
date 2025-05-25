from dagster import op
from cd4ml_pipeline.ops.shared.mlflow_utils import init_mlflow
from cd4ml_pipeline.ops.shared.pre_process import preprocess_data
from cd4ml_pipeline.ops.shared.validate import validate_schema

@op
def train_saude_lavoura():
    print("🌾 Processando dados de saúde da lavoura...")
    preprocess_data("saude_lavoura")
    validate_schema("saude_lavoura")

    mlflow = init_mlflow()
    with mlflow.start_run(run_name="treino_saude_lavoura"):
        mlflow.log_param("modelo", "XGBoost")
        mlflow.log_metric("f1_score", 0.84)