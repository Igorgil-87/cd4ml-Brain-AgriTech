from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel
from app.kafka.producer import send_to_kafka
from app.security.api_key import validate_api_key

# Produtividade
router_prod = APIRouter(
    prefix="/produtividade",
    tags=["Produtividade"],
    dependencies=[Depends(validate_api_key)]  # Proteção com API_KEY
)

class SoloInput(BaseModel):
    tipo_solo: str
    ph: float

@router_prod.post("/solo")
def solo_view(request: Request, data: SoloInput):
    result = {"classificacao": "fértil"}
    send_to_kafka({
        "endpoint": "/produtividade/solo",
        "input": data.dict(),
        "ip": request.client.host,
        "resultado": result
    })
    return result

@router_prod.post("/ndvi")
def ndvi_view(request: Request):
    result = {"ndvi": 0.79}
    send_to_kafka({
        "endpoint": "/produtividade/ndvi",
        "input": {},
        "ip": request.client.host,
        "resultado": result
    })
    return result

@router_prod.post("/safrahistorica")
def safrahistorica_view(request: Request):
    result = {"rendimento_medio": 52.3}
    send_to_kafka({
        "endpoint": "/produtividade/safrahistorica",
        "input": {},
        "ip": request.client.host,
        "resultado": result
    })
    return result

@router_prod.post("/otimizacaoInsumo")
def otimizacao_view(request: Request):
    result = {"resultado": "Aplicar 15% menos NPK"}
    send_to_kafka({
        "endpoint": "/produtividade/otimizacaoInsumo",
        "input": {},
        "ip": request.client.host,
        "resultado": result
    })
    return result

@router_prod.post("/pred_rendimento")
def pred_rendimento_view(request: Request):
    result = {"previsao_rendimento": 65.2}
    send_to_kafka({
        "endpoint": "/produtividade/pred_rendimento",
        "input": {},
        "ip": request.client.host,
        "resultado": result
    })
    return result

@router_prod.post("/penalizacao")
def penalizacao_produtividade_view(request: Request):
    result = {"alerta": "Sem penalizações recentes"}
    send_to_kafka({
        "endpoint": "/produtividade/penalizacao",
        "input": {},
        "ip": request.client.host,
        "resultado": result
    })
    return result