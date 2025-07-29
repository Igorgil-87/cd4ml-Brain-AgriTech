from fastapi import FastAPI
from app.routes import (
    rendimento,
    commodities,
    insumo,
    saude_lavoura,
    seguros,
    produtividade,
    socioambiental,
    logistica,
    geografico,
    imagens
)
from app.security.api_key import APIKeyValidatorMiddleware

app = FastAPI(
    title="API CD4ML Agro",
    description="Serviço de inferência de modelos de machine learning aplicados ao agronegócio.",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc"      # Redoc UI
)

# Middleware de segurança via API Key
app.add_middleware(APIKeyValidatorMiddleware)

# Registro de todas as rotas
app.include_router(rendimento.router, tags=["Rendimento"])
app.include_router(commodities.router, tags=["Commodities"])
app.include_router(insumo.router, tags=["Insumo"])
app.include_router(saude_lavoura.router, tags=["Saúde da Lavoura"])
app.include_router(seguros.router_seguros, tags=["Seguros"])
app.include_router(produtividade.router_prod, tags=["Produtividade"])
app.include_router(socioambiental.router_socio, tags=["Socioambiental"])
app.include_router(logistica.router_logistica, tags=["Logística"])
app.include_router(geografico.router, tags=["Geográfico"])
app.include_router(imagens.router_imagens, tags=["Imagens"])

# Endpoint raiz
@app.get("/", tags=["Status"])
def root():
    return {"message": "API CD4ML online - consulte /docs para mais informações"}