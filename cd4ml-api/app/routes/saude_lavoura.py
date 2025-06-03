from fastapi import APIRouter
from app.mlflow_client import load_model, predict

router = APIRouter()

@router.post("/saude_lavoura/predict")
def predict_saude(input_data: dict):
    model = load_model("saude_lavoura")
    result = predict(model, input_data)
    return {"indicador_previsto": result}