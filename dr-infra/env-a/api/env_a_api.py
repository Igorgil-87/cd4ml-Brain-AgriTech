from fastapi import FastAPI
from fastapi.responses import JSONResponse
import subprocess
import os
from pathlib import Path

app = FastAPI()

# Local do docker-compose.yaml
BASE_DIR = Path(__file__).resolve().parents[1]  # .../dr-infra/env-a
COMPOSE_FILE = os.environ.get("COMPOSE_FILE", str(BASE_DIR / "docker-compose.yaml"))


def run_compose(cmd: list[str]) -> dict:
    """Executa docker compose com o arquivo definido"""
    try:
        result = subprocess.run(
            ["docker", "compose", "-f", COMPOSE_FILE] + cmd,
            capture_output=True,
            text=True,
            check=False
        )
        return {
            "rc": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except Exception as e:
        return {"rc": 1, "stdout": "", "stderr": str(e)}


@app.get("/status")
def status():
    """Checa se o docker-compose.yaml existe e retorna ps"""
    if not Path(COMPOSE_FILE).exists():
        return JSONResponse(content={"ok": False, "error": f"{COMPOSE_FILE} não encontrado"})
    ps = run_compose(["ps"])
    return JSONResponse(content={"ok": ps["rc"] == 0, "ps": ps})


@app.post("/start")
def start():
    """Sobe os containers"""
    if not Path(COMPOSE_FILE).exists():
        return JSONResponse(content={"ok": False, "error": f"{COMPOSE_FILE} não encontrado"})
    up = run_compose(["up", "-d"])
    return JSONResponse(content={"ok": up["rc"] == 0, "result": up})


@app.post("/stop")
def stop():
    """Para os containers"""
    if not Path(COMPOSE_FILE).exists():
        return JSONResponse(content={"ok": False, "error": f"{COMPOSE_FILE} não encontrado"})
    down = run_compose(["down"])
    return JSONResponse(content={"ok": down["rc"] == 0, "result": down})