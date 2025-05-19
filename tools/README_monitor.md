# 🔍 Monitor Jenkins - CD4ML Brain AgriTech

Este script (`monitor_jenkins.py`) é usado para monitorar o status da última execução do job do Jenkins e emitir alertas em caso de falha.

---

## ⚙️ Como usar

1. Configure suas variáveis no topo do script:
   ```python
   JENKINS_URL = "http://localhost:10000"
   JOB_NAME = "cd4ml-Brain-AgriTech"
   USER = "admin"
   API_TOKEN = "seu-token-aqui"