from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.mlflow_client import ModelClient

router = APIRouter()
client = ModelClient()

class InsumoInput(BaseModel):
    ano: int
    uf: str
    unidade: str
    cultura: str

@router.post("/predict/insumo")
def predict_insumo(data: InsumoInput):
    try:
        result = client.predict("insumo", data.dict())
        return {"resultado": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))