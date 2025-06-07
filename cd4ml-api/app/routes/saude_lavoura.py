from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.mlflow_client import ModelClient

router = APIRouter()
client = ModelClient()

class SaudeLavouraInput(BaseModel):
    ano: int
    uf: str
    unidade: str
    cultura: str

@router.post("/predict/saude-lavoura")
def predict_saude_lavoura(data: SaudeLavouraInput):
    try:
        result = client.predict("saude_lavoura", data.dict())
        return {"resultado": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))