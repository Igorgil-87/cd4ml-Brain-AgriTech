from fastapi import APIRouter, Request, Depends
from app.kafka.producer import send_to_kafka
from app.security.api_key import validate_api_key

# Logística
router_logistica = APIRouter(
    prefix="/logistica",
    tags=["Logística"],
    dependencies=[Depends(validate_api_key)]  # Proteção com API_KEY
)

@router_logistica.post("/logistica")
def logistica_view(request: Request):
    result = {
        "infraestrutura": "Moderada",
        "acesso": "Rodovia duplicada"
    }
    send_to_kafka({
        "endpoint": "/logistica/logistica",
        "input": {},
        "ip": request.client.host,
        "resultado": result
    })
    return result

@router_logistica.post("/lavoura")
def lavoura_view(request: Request):
    result = {
        "distancia_mercado": "45 km",
        "modal": "rodoviário"
    }
    send_to_kafka({
        "endpoint": "/logistica/lavoura",
        "input": {},
        "ip": request.client.host,
        "resultado": result
    })
    return result