from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel
from app.kafka.producer import send_to_kafka
from app.security.api_key import validate_api_key

# Geográfico
router = APIRouter(
    prefix="/geografico",
    tags=["Geográfico"],
    dependencies=[Depends(validate_api_key)]  # Protege todas as rotas abaixo
)

class CarGeoInput(BaseModel):
    municipio: str
    estado: str

@router.post("/car_geo")
def car_geo_view(request: Request, data: CarGeoInput):
    result = {"area_total": "1200 ha", "codigo_imovel": "CAR123456"}
    send_to_kafka({
        "endpoint": "/geografico/car_geo",
        "input": data.dict(),
        "ip": request.client.host,
        "resultado": result
    })
    return result

@router.post("/colheita")
def colheita_view(request: Request):
    result = {"coordenadas": "Lat:-12.345, Lon:-54.321"}
    send_to_kafka({
        "endpoint": "/geografico/colheita",
        "input": {},
        "ip": request.client.host,
        "resultado": result
    })
    return result