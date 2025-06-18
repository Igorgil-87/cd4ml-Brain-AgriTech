from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.mlflow_client import ModelClient
import random
import datetime

router = APIRouter()
client = ModelClient()

class RendimentoInput(BaseModel):
    ano: int
    uf: str
    unidade: str
    cultura: str

@router.post("/predict/rendimento")
def predict_rendimento(data: RendimentoInput):
    try:
        # Gera features artificiais esperadas pelo modelo
        entrada_modelo = {
            "ano": data.ano,
            "mes": datetime.datetime.now().month,  # ou usar lógica da cultura
            "mediaEst": round(random.uniform(40.0, 80.0), 2),
            "mediaNac": round(random.uniform(45.0, 85.0), 2)
        }

        result = client.predict("rendimento", entrada_modelo)
        return {
            "input_recebido": data.dict(),
            "features_utilizadas": entrada_modelo,
            "resultado": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))