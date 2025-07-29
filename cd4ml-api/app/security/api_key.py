import os
from dotenv import load_dotenv
from fastapi import Request, HTTPException, status

load_dotenv()  # Carrega variáveis do .env

API_KEY = os.getenv("API_KEY")

def validate_api_key(request: Request):
    client_key = request.headers.get("X-API-KEY")
    if client_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chave de API inválida ou ausente"
        )