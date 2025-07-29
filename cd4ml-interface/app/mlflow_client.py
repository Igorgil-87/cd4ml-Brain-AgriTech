import mlflow.pyfunc
import mlflow
import os

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:12000")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

def load_model(model_name: str, stage: str = "Production"):
    """
    Carrega um modelo registrado no MLflow Model Registry pelo nome e estágio.
    """
    model_uri = f"models:/{model_name}/{stage}"
    return mlflow.pyfunc.load_model(model_uri)

def predict(model, input_data: dict):
    """
    Realiza predição com base no input_data recebido (formulário ou JSON).
    Converte para DataFrame internamente.
    """
    import pandas as pd

    df = pd.DataFrame([input_data])
    prediction = model.predict(df)

    # Retorna como string (JSON serializável)
    return prediction[0] if len(prediction) == 1 else prediction.tolist()