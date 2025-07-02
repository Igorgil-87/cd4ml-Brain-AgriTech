import mlflow
import os

model_name = os.getenv("MODEL_NAME", "rendimento")
stage_name = "Production"

try:
    client = mlflow.tracking.MlflowClient()
    versions = client.get_latest_versions(name=model_name, stages=[stage_name])

    if versions:
        print("new_model_found")
    else:
        print("")  # Nada encontrado

except Exception as e:
    print(f"Erro ao consultar modelo: {e}")
    exit(1)