from fastapi import APIRouter
from app.mlflow_client import load_model, predict

router = APIRouter()

@router.post("/insumo/predict")
def predict_insumo(input_data: dict):
    model = load_model("insumo")
    result = predict(model, input_data)
    return {"gasto_previsto": result}