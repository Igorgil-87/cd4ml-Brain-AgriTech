from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel
from app.kafka.producer import send_to_kafka
from app.security.api_key import validate_api_key

# Seguros
router_seguros = APIRouter(
    prefix="/seguros",
    tags=["Seguros"],
    dependencies=[Depends(validate_api_key)]  # Proteção com API_KEY
)

class IBAMAInput(BaseModel):
    cnpj: str
    atividade: str

@router_seguros.post("/IBAMA")
def ibama_view(request: Request, body: IBAMAInput):
    result = {"resultado": "risco médio"}
    send_to_kafka({
        "endpoint": "/seguros/IBAMA",
        "input": body.dict(),
        "ip": request.client.host,
        "resultado": result
    })
    return result

class PenalizacaoInput(BaseModel):
    cpf: str
    tipo_pessoa: str

@router_seguros.post("/penalizacao")
def penalizacao_view(request: Request, data: PenalizacaoInput):
    result = {"penalizado": False, "detalhes": "Sem registros"}
    send_to_kafka({
        "endpoint": "/seguros/penalizacao",
        "input": data.dict(),
        "ip": request.client.host,
        "resultado": result
    })
    return result

class GeodesicaInput(BaseModel):
    latitude: float
    longitude: float

@router_seguros.post("/geodesica")
def geodesica_view(request: Request, data: GeodesicaInput):
    result = {"utm": "23K 674389 9020341"}
    send_to_kafka({
        "endpoint": "/seguros/geodesica",
        "input": data.dict(),
        "ip": request.client.host,
        "resultado": result
    })
    return result

@router_seguros.post("/incendio")
def incendio_view(request: Request):
    result = {"risco": "moderado", "alerta": True}
    send_to_kafka({
        "endpoint": "/seguros/incendio",
        "input": {},
        "ip": request.client.host,
        "resultado": result
    })
    return result

@router_seguros.post("/score_gove")
def score_gove_view(request: Request):
    result = {"score": 87, "nível": "Alto"}
    send_to_kafka({
        "endpoint": "/seguros/score_gove",
        "input": {},
        "ip": request.client.host,
        "resultado": result
    })
    return result