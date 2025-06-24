import mlflow
import mlflow.pyfunc
import pandas as pd
from typing import Dict, Any
import os

class ModelClient:
    def __init__(self):
        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
        mlflow.set_tracking_uri(tracking_uri)
        self.models = {}

    def load_model(self, model_name: str, stage: str = "Production") -> mlflow.pyfunc.PyFuncModel:
        model_uri = f"models:/{model_name}/{stage}"
        model_key = f"{model_name}_{stage}"

        if model_key not in self.models:
            try:
                print(f"[INFO] Carregando modelo: {model_uri}")
                model = mlflow.pyfunc.load_model(model_uri)
                self.models[model_key] = model
            except Exception as e:
                print(f"[ERRO] Falha ao carregar modelo '{model_name}' no estágio '{stage}': {e}")
                raise
        return self.models[model_key]

    def predict(self, model_name: str, data: Dict[str, Any], stage: str = "Production") -> Any:
        model_key = f"{model_name}_{stage}"
        if model_key not in self.models:
            self.load_model(model_name, stage)
        model = self.models[model_key]
        df = pd.DataFrame([data])
        try:
            prediction = model.predict(df)
            return prediction.tolist()
        except Exception as e:
            print(f"[ERRO] Falha na predição com modelo '{model_name}': {e}")
            raise
