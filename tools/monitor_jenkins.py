import requests
import time
from datetime import datetime

JENKINS_URL = "http://localhost:10000"
JOB_NAME = "cd4ml-Brain-AgriTech"
USER = "admin"
API_TOKEN = "seu-token-aqui"  # substitua pelo seu token de API

def get_last_build_status():
    url = f"{JENKINS_URL}/job/{JOB_NAME}/lastBuild/api/json"
    try:
        response = requests.get(url, auth=(USER, API_TOKEN), timeout=10)
        response.raise_for_status()
        data = response.json()
        return data['result'], data['timestamp']
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Erro ao consultar Jenkins: {e}")
        return None, None

if __name__ == "__main__":
    while True:
        status, ts = get_last_build_status()
        if status:
            print(f"[{datetime.now()}] ✅ Última build: {status}")
            if status != "SUCCESS":
                print("❌ ALERTA: Última execução falhou!")
        else:
            print(f"[{datetime.now()}] 🔄 Jenkins inacessível ou sem builds.")
        time.sleep(300)  # a cada 5 minutos