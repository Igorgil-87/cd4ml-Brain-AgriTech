from fastapi import FastAPI
from app.routes import rendimento, commodities, insumo, saude_lavoura

app = FastAPI(title="CD4ML API")

app.include_router(rendimento.router)
app.include_router(commodities.router)
app.include_router(insumo.router)
app.include_router(saude_lavoura.router)

@app.get("/")
def root():
    return {"message": "API CD4ML online"}