TIMESTAMP := $(shell date +%Y%m%d_%H%M%S)
LOG_DIR := logs

.PHONY: logs

logs:
	mkdir -p $(LOG_DIR)

run:
	make logs
	@echo ">>> Executando pipeline..."
	python3 run_python_script.py pipeline $(PROBLEM) $(PIPELINE_PARAMS) $(FEATURE_SET) $(ALGORITHM) $(ALGORITHM_PARAMS) \
		2>&1 | tee $(LOG_DIR)/run_$(TIMESTAMP).log

test:
	make logs
	@echo ">>> Executando testes..."
	pytest cd4ml/problems/$(PROBLEM)/tests --maxfail=2 --disable-warnings --tb=short \
		2>&1 | tee $(LOG_DIR)/test_$(TIMESTAMP).log

summary:
	make logs
	@echo ">>> Gerando resumo da execução..."
	@echo "PIPELINE SUMMARY - $(TIMESTAMP)" > $(LOG_DIR)/pipeline_summary_$(TIMESTAMP).txt
	@echo "Problem: $(PROBLEM)" >> $(LOG_DIR)/pipeline_summary_$(TIMESTAMP).txt
	@echo "Feature Set: $(FEATURE_SET)" >> $(LOG_DIR)/pipeline_summary_$(TIMESTAMP).txt
	@echo "Algorithm: $(ALGORITHM)" >> $(LOG_DIR)/pipeline_summary_$(TIMESTAMP).txt
	@echo "MLflow Tracking: $(MLFLOW_TRACKING_URL)" >> $(LOG_DIR)/pipeline_summary_$(TIMESTAMP).txt