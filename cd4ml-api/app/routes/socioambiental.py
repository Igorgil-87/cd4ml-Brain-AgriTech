from fastapi import APIRouter, Request, Depends
from app.kafka.producer import send_to_kafka
from app.security.api_key import validate_api_key

# Socioambiental
router_socio = APIRouter(
    prefix="/socioambiental",
    tags=["Socioambiental"],
    dependencies=[Depends(validate_api_key)]  # Proteção com API_KEY
)

@router_socio.post("/bioma")
def bioma_view(request: Request):
    result = {"bioma": "Cerrado"}
    send_to_kafka({
        "endpoint": "/socioambiental/bioma",
        "input": {},
        "ip": request.client.host,
        "resultado": result
    })
    return result

@router_socio.post("/incendio_socio")
def incendio_socio_view(request: Request):
    result = {"nivel_risco": "Alto"}
    send_to_kafka({
        "endpoint": "/socioambiental/incendio_socio",
        "input": {},
        "ip": request.client.host,
        "resultado": result
    })
    return result

@router_socio.post("/unidade_conservacao_socio")
def uc_view(request: Request):
    result = {"proxima_uc": "Parque Estadual da Serra Azul"}
    send_to_kafka({
        "endpoint": "/socioambiental/unidade_conservacao_socio",
        "input": {},
        "ip": request.client.host,
        "resultado": result
    })
    return result

@router_socio.post("/indigina_socio")
def indigina_view(request: Request):
    result = {"proxima_terra_indigena": "TI Xavante"}
    send_to_kafka({
        "endpoint": "/socioambiental/indigina_socio",
        "input": {},
        "ip": request.client.host,
        "resultado": result
    })
    return result