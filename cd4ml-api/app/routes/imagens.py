from fastapi import APIRouter, Request, Depends
from app.kafka.producer import send_to_kafka
from app.security.api_key import validate_api_key

# Imagens
router_imagens = APIRouter(
    prefix="/imagens",
    tags=["Imagens"],
    dependencies=[Depends(validate_api_key)]  # Protege com API_KEY
)

@router_imagens.post("/satellite")
def satellite_view(request: Request):
    result = {
        "imagem": "https://fakecdn.com/sentinel/area123.png",
        "data": "2025-07-18"
    }
    send_to_kafka({
        "endpoint": "/imagens/satellite",
        "input": {},
        "ip": request.client.host,
        "resultado": result
    })
    return result