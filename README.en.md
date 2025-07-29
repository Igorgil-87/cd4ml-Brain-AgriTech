# CD4ML Brain AgriTech - Infrastructure & MLOps (EN)

This repository contains the full infrastructure setup for the **CD4ML (Continuous Delivery for Machine Learning)** project in the agribusiness domain. It integrates several services—such as Jenkins, Dagster, MLflow, MinIO, Spinnaker, Airflow, Kafka, PostgreSQL, and others—via Docker Compose to support automated pipelines, model deployment, monitoring, and disaster recovery.

## 🔍 Overview

This system implements a complete MLOps ecosystem, supporting the lifecycle of machine learning models from experimentation to production. It includes:

- Continuous Integration with Jenkins
- Continuous Delivery & Orchestration with Dagster, Spinnaker and Airflow
- Model tracking and artifact management with MLflow + MinIO (S3-compatible)
- Logging and Monitoring with Fluentd + Elasticsearch + Kibana
- Visual UI with Flask Interface and JupyterLab for notebooks
- Kafka/Zookeeper for streaming events
- PostgreSQL & PgAdmin for data persistence
- Full Disaster Recovery support with Spinnaker (DSR approach)

## 📦 Services

| Component       | Description |
|----------------|-------------|
| **Jenkins**     | CI server orchestrating tests, builds, and deployments. |
| **Dagster**     | Data orchestrator for machine learning pipelines. |
| **Airflow**     | Workflow scheduler and DAG manager. |
| **Spinnaker**   | CD platform used for disaster recovery strategies and deployments. |
| **MLflow**      | Experiment tracking and model registry. |
| **MinIO**       | S3-compatible artifact storage (used by MLflow). |
| **Fluentd + Kibana + ElasticSearch** | Centralized logging and log visualization. |
| **Kafka + Zookeeper** | Stream and event backbone for ML/DS pipelines. |
| **JupyterLab**  | Interactive data science IDE. |
| **PostgreSQL + PgAdmin** | Database backend for MLflow and Airflow. |
| **Flask Interface** | Frontend for accessing model APIs and dashboards. |

## 🛠️ How to Start

1. Clone the repository:

```bash
git clone https://github.com/Igorgil-87/cd4ml-Brain-AgriTech.git
cd cd4ml-Brain-AgriTech
```

2. Set environment variables:

```bash
export ACCESS_KEY=your_access_key
export SECRET_KEY=your_secret_key
```

3. Start the environment:

```bash
docker-compose up -d
```

## ✅ Monitoring & Health

- Jenkins: [http://localhost:10000](http://localhost:10000)
- MLflow: [http://localhost:12000](http://localhost:12000)
- MinIO: [http://localhost:9000](http://localhost:9000)
- Kibana: [http://localhost:5601](http://localhost:5601)
- Jupyter: [http://localhost:8888](http://localhost:8888)
- Interface Flask: [http://localhost:11001](http://localhost:11001)

## 🚀 CI/CD Examples with Make

```bash
make install            # install dependencies
make test PROBLEM=x     # run pytest
make run PROBLEM=x      # run full pipeline for a model
make acceptance         # run acceptance tests
make register-model     # register model in MLflow
make deploy             # deploy model using Docker
```

## 🔁 Tear Down and Recreate

To destroy and recreate the full Spinnaker cluster:

```bash
./destroy_spinnaker.sh
./setup_spinnaker.sh
```

## 📂 Directory Layout

```
cd4ml-Brain-AgriTech/
├── cd4ml-api/                 # FastAPI model serving
├── cd4ml-interface/           # Flask dashboard
├── dagster/                   # Dagster pipelines & sensors
├── airflow/                   # DAGs and configs for Airflow
├── jenkins/                   # Jenkins Dockerfile & pipeline scripts
├── data/, scripts/, notebooks/, fluentd/ etc.
```

## 📘 Additional

- Healthchecks are embedded in docker-compose
- Slack alert integration for Dagster jobs
- PostgreSQL and MinIO volumes are persistent
- Disaster Recovery is automated through Spinnaker + Halyard + KIND
- Multi-model support: rendimento, commodities, insumo, saúde da lavoura

---

This infrastructure was designed to support real-time, resilient, and production-grade machine learning for the agricultural sector.