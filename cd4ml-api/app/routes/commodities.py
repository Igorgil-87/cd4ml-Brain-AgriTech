from fastapi import APIRouter
from app.mlflow_client import load_model, predict

router = APIRouter()

@router.post("/commodities/predict")
def predict_commodities(input_data: dict):
    model = load_model("commodities")
    result = predict(model, input_data)
    return {"media_prevista": result}