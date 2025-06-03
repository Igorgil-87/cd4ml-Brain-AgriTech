from fastapi import APIRouter
from app.mlflow_client import load_model, predict

router = APIRouter()

@router.post("/rendimento/predict")
def predict_rendimento(input_data: dict):
    model = load_model("rendimento")
    result = predict(model, input_data)
    return {"rendimento_previsto": result}