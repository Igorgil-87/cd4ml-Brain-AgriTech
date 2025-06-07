from fastapi import APIRouter, HTTPException
from app.mlflow_client import ModelClient
from pydantic import BaseModel

router = APIRouter()
client = ModelClient()

class CommodityInput(BaseModel):
    ano: int
    uf: str
    unidade: str
    cultura: str

@router.post("/predict/commodities")
def predict_commodities(data: CommodityInput):
    try:
        result = client.predict("commodities", data.dict())
        return {"resultado": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))