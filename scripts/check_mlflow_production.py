import mlflow

mlflow.set_tracking_uri("http://mlflow:5000")  # ou o endpoint do MLflow no Jenkins
client = mlflow.MlflowClient()

model_name = "rendimento"
try:
    latest_versions = client.get_latest_versions(name=model_name, stages=["Production"])
    print("✔️ Modelo encontrado:", latest_versions)
except Exception as e:
    print(f"Erro ao consultar modelo: {e}")
    exit(1)