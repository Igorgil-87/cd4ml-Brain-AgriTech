from fastapi import FastAPI
from app.routes import rendimento, commodities, insumo, saude_lavoura

app = FastAPI(
    title="API CD4ML Agro",
    description="Serviço de inferência de modelos de machine learning aplicados ao agronegócio.",
    version="1.0.0",
    docs_url="/docs",       # Swagger
    redoc_url="/redoc"      # Redoc
)

# Inclui os endpoints de cada modelo
app.include_router(rendimento.router, tags=["Rendimento"])
app.include_router(commodities.router, tags=["Commodities"])
app.include_router(insumo.router, tags=["Insumo"])
app.include_router(saude_lavoura.router, tags=["Saúde da Lavoura"])

# Endpoint raiz
@app.get("/", tags=["Status"])
def root():
    return {"message": "API CD4ML online - consulte /docs para mais informações"}