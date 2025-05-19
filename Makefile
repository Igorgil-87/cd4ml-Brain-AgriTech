# ========== VARIÁVEIS ==========
PYTHON := python3
PROBLEM ?= rendimento
PIPELINE_PARAMS ?= default
FEATURE_SET ?= default
ALGORITHM ?= default
ALGORITHM_PARAMS ?= default
MLFLOW_TRACKING_URL ?= http://mlflow:5000

# ========== ALVOS ==========

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

test:
	pytest cd4ml/problems/$(PROBLEM)/tests --maxfail=2 --disable-warnings --tb=short

run:
	$(PYTHON) run_python_script.py pipeline $(PROBLEM) $(PIPELINE_PARAMS) $(FEATURE_SET) $(ALGORITHM) $(ALGORITHM_PARAMS)

acceptance:
	$(PYTHON) run_python_script.py acceptance

register-model:
	$(PYTHON) run_python_script.py register_model $(MLFLOW_TRACKING_URL) yes

deploy:
	@echo "Reiniciando container 'model' se estiver presente..."
	docker ps -a --format '{{.Names}}' | grep -q '^model$$' && docker restart model || echo "Container 'model' não encontrado."

all: install test run acceptance register-model deploy