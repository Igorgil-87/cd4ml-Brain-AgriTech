import mlflow
import pandas as pd
from app.config import MLFLOW_TRACKING_URI

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

def load_model(model_name: str):
    model_uri = f"models:/{model_name}/latest"
    return mlflow.pyfunc.load_model(model_uri)

def predict(model, input_data: dict):
    df = pd.DataFrame([input_data])
    prediction = model.predict(df)
    return prediction[0]