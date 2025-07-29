# CD4ML Brain AgriTech 🇧🇷

Repositório oficial do projeto **CD4ML - Continuous Delivery for Machine Learning** voltado ao setor agro da Brain AgriTech. Este ambiente Docker Compose orquestra uma arquitetura completa para desenvolvimento, treinamento, implantação e monitoramento de modelos de machine learning com foco em governança, segurança e escalabilidade.

---

## 🚜 Visão Geral do Projeto

O objetivo é garantir **previsibilidade, automação e confiabilidade** no ciclo de vida de modelos de ML. Isso é alcançado por meio de uma arquitetura modular que une:

- Pipelines CI/CD automatizados com Jenkins
- Orquestração de jobs com Dagster e Airflow
- Gerenciamento de experimentos com MLflow
- Deploy e rollback com Spinnaker
- Monitoramento com Kibana, Fluentd e ElasticSearch
- Armazenamento com MinIO (S3-compatible)
- Exposição de APIs com FastAPI e interface Flask
- Suporte à escalabilidade com Kafka e PostgreSQL

---

## 🔧 Serviços Incluídos

| Serviço       | Porta     | Descrição |
|---------------|-----------|-----------|
| Jenkins       | 10000     | CI/CD, integração com GitHub, Spinnaker |
| Dagster       | 3005      | Orquestração de pipelines de ML |
| MLflow        | 12000     | Rastreamento e registro de modelos |
| MinIO         | 9000/9001 | Armazenamento de artefatos (S3) |
| Airflow       | 8083      | Agendamento de jobs (Batch/ETL) |
| Jupyter       | 8888      | Desenvolvimento interativo |
| Kafka/Zoo     | 9092/2181 | Mensageria para eventos e dados |
| Interface     | 11001     | Frontend unificado via Flask |
| Kibana        | 5601      | Observabilidade e análise de logs |
| PgAdmin       | 8081      | Gerenciador do PostgreSQL |
| Spinnaker     | via Ingress| Deploy, rollback e Disaster Recovery |

---

## ⚙️ Pré-requisitos

- Docker e Docker Compose
- Python 3.11 (para scripts locais)
- Variáveis de ambiente (coloque no `.env`):
  ```bash
  MINIO_ACCESS_KEY=minioadmin
  MINIO_SECRET_KEY=minioadmin
  POSTGRES_USER=agro_user
  POSTGRES_PASSWORD=agro_password
  ```

---

## 🚀 Como Subir o Ambiente

```bash
# Clone o projeto
git clone https://github.com/Igorgil-87/cd4ml-Brain-AgriTech.git
cd cd4ml-Brain-AgriTech

# Suba todos os serviços
docker-compose up -d

# Acesse a interface principal
http://localhost:11001
```

---

## 🧪 Testes & Pipelines (CI/CD)

```bash
# Instalar dependências e hooks
make install

# Executar testes automatizados
make test PROBLEM=rendimento

# Rodar pipeline completo
make run PROBLEM=insumo

# Registrar modelo no MLflow
make register-model
```

---

## 🔄 Tear Down & Reset Total

Para destruir e reconstruir todo o ambiente (inclusive o Spinnaker):

```bash
./scripts/destroy_and_recreate.sh
```

---

## 🧠 Estrutura de Pastas

```
├── dagster/              # Jobs e ops de ML
├── airflow/dags/         # DAGs do Airflow
├── cd4ml-api/            # API FastAPI dos modelos
├── cd4ml-interface/      # Frontend Flask unificado
├── jenkins/              # Configs do Jenkins
├── scripts/              # Utilitários e teardown
├── data/                 # Dados de entrada
├── fluentd/              # Logs para ElasticSearch
└── docker-compose.yml    # Orquestração principal
```

---

## 📈 Observabilidade & Alertas

- Todos os logs são roteados para o ElasticSearch via Fluentd
- Alertas do Dagster via Slack (token no `.env`)
- Healthcheck em todos os containers críticos

---

## 🛡️ Disaster Recovery

- O Spinnaker é utilizado para deploy e rollback
- Configuração pronta para ambientes A/B locais
- Suporte a futuros DR na cloud

---

## 👥 Colaborando

Pull requests são bem-vindos! Documente seu código, siga as boas práticas e mantenha os padrões do projeto.

---

## 📄 Licença

MIT © Igor Gil — Santander Financiamentos