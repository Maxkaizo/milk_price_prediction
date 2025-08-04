# Makefile minimalista para MLflow y Prefect

# Variables
MLFLOW_DIR = mlflow
LOGS_DIR = logs
MLFLOW_LOG = $(LOGS_DIR)/mlflow.log
MLFLOW_PID = $(LOGS_DIR)/mlflow.pid
FLOW_FILE = orchestration/flows/master_daily_flow.py

# MLflow targets
start-mlflow:
	cd $(MLFLOW_DIR) && nohup mlflow server \
		--backend-store-uri=sqlite:///mlflow.db \
		--default-artifact-root=s3://mlflow-models-milk-price-dev \
		--host 0.0.0.0 --port 5000 \
		> ../$(MLFLOW_LOG) 2>&1 & \
	ps -ef | grep mlflow | head -n 2 | tail -n 1 | cut -d" " -f 4 > $(MLFLOW_PID)

stop-mlflow:
	kill $$(cat $(MLFLOW_PID)) 2>/dev/null || echo "MLflow no está ejecutándose"

# Prefect targets
start-prefect:
	prefect server start --background

stop-prefect:
	prefect server stop

# Deploy y run de flows
deploy-flow:
	python $(FLOW_FILE) &

run-flow:
	prefect deployment run 'daily-mlops-pipeline/daily-milk-predictor'

run-flow-date:
	@read -p "Ingresa la fecha (YYYY-MM-DD): " date; \
	prefect deployment run 'daily-mlops-pipeline/daily-milk-predictor' \
		--param execution_date="$$date"

# Validación y monitoreo
check-mlflow:
	curl -s http://localhost:5000/health || echo "MLflow no responde"

check-prefect:
	curl -s http://localhost:4200/api/health || echo "Prefect no responde"

logs-mlflow:
	tail -f $(MLFLOW_LOG )

status:
	@echo "=== Estado de los servicios ==="
	@echo "MLflow:"
	@ps aux | grep mlflow | grep -v grep || echo "  No ejecutándose"
	@echo "Prefect:"
	@ps aux | grep prefect | grep -v grep || echo "  No ejecutándose"

# Targets de ayuda
help:
	@echo "Targets disponibles:"
	@echo "  start-mlflow     - Iniciar servidor MLflow en background"
	@echo "  stop-mlflow      - Detener servidor MLflow"
	@echo "  start-prefect    - Iniciar servidor Prefect en background"
	@echo "  stop-prefect     - Detener servidor Prefect"
	@echo "  deploy-flow      - Desplegar el flow principal"
	@echo "  run-flow         - Ejecutar el flow manualmente"
	@echo "  run-flow-date    - Ejecutar el flow con fecha específica"
	@echo "  check-mlflow     - Verificar estado de MLflow"
	@echo "  check-prefect    - Verificar estado de Prefect"
	@echo "  logs-mlflow      - Ver logs de MLflow en tiempo real"
	@echo "  status           - Ver estado de todos los servicios"
	@echo "  help             - Mostrar esta ayuda"

.PHONY: start-mlflow stop-mlflow start-prefect stop-prefect deploy-flow run-flow run-flow-date check-mlflow check-prefect logs-mlflow status help
