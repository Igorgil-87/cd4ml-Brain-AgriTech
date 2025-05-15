# 🌽 CD4ML Agro

Este projeto implementa um pipeline completo de **Continuous Delivery for Machine Learning (CD4ML)** para o setor **Agro**, focado em previsões como preços de commodities, uso de insumos e rendimento de lavouras.

## 📌 Objetivo

Automatizar o ciclo completo de Machine Learning:
- Ingestão e transformação de dados agrícolas
- Treinamento de modelos supervisionados
- Validação automatizada
- Registro em MLflow
- Disponibilização via API Flask com Swagger
- Orquestração com Docker e Jenkins

---

## ⚙️ Arquitetura Geral

![CD4ML Agro Architecture](A_flowchart_diagram_depicts_a_CD4ML_(Continuous_De.png)

---

## 🧱 Componentes

### 🔸 Ingestão de Dados
- **load_data.py**: Carrega dados climáticos, produtividade, uso de insumos e registros por cultura para o PostgreSQL
- **MinIO**: Armazena artefatos de modelo (backup opcional)

### 🔸 Feature Engineering
- **FeatureSet**: Define e transforma features categóricas e numéricas
- **Encoder**: One-hot encoding com suporte a omissões e estatísticas

### 🔸 Treinamento de Modelos
- **MLModel**: Classe que encapsula modelo, encoder e predições
- **train.py**: Treinamento supervisionado com suporte a múltiplos algoritmos

### 🔸 Validação & Registro
- **splitter.py**: Split determinístico baseado em hashing + seed
- **register_model.py**: Publica modelo, métricas e parâmetros no MLflow

### 🔸 APIs e Visualização
- **app.py**: API Flask para servir previsões por cenário (`/api/commodities/predict`, etc.)
- **Swagger**: Documentação automática
- **Kibana**: Logs de inferência e eventos via Fluentd

---

## 🧪 Casos de Uso Atuais

- `commodities`: Previsão de preço futuro com base em cultura, região e área
- `insumo`: Otimização do uso de insumos agrícolas
- `rendimento`: Estimativa de produtividade da lavoura
- `saude_lavoura`: Classificação do estado das plantações

---

## 🚀 Rodando Localmente

```bash
# Ingestão de dados
python load_data.py

# Pipeline completo
python run_python_script.py pipeline commodities

# Registro
python run_python_script.py register_model http://localhost:5000 yes <model_id>
```

---

## 📦 Infraestrutura

- Docker + Docker Compose
- Jenkins
- MLflow + MinIO
- PostgreSQL
- Flask
- Airflow (orquestração futura)

---

## 🔜 Próximas Melhorias

- Integração com Great Expectations para validação de dados
- Geração de explicabilidade com SHAP
- Deploy via Gunicorn + NGINX
- Adição de novos cenários: produção sustentável, risco climático, etc.

---

## 🏆 Reconhecimentos

Projeto finalista nos prêmios de inovação  **AgTech Awards**.