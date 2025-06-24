from fastapi import APIRouter, HTTPException, Query
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
def predict_rendimento(data: RendimentoInput, stage: str = Query("Production")):
    try:
        entrada_modelo = {
            "ano": data.ano,
            "mes": datetime.datetime.now().month,
            "mediaEst": round(random.uniform(40.0, 80.0), 2),
            "mediaNac": round(random.uniform(45.0, 85.0), 2)
        }

        result = client.predict("rendimento", entrada_modelo, stage=stage)
        return {
            "input_recebido": data.dict(),
            "features_utilizadas": entrada_modelo,
            "stage_utilizado": stage,
            "resultado": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@router.post("/promote_model")
def promote_model(model_name: str = Query(...), r2_score: float = Query(...), threshold: float = Query(0.8)):
    try:
        from app.mlflow_utils import promote_model_if_good_score
        promote_model_if_good_score(model_name, r2_score, threshold)
        return {"message": f"Verificação realizada para promoção do modelo '{model_name}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
