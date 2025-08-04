# Makefile for MLOps Project - Milk Price Prediction
# Based on development process notes

# Configuration variables
PYTHON = python
PIPENV = pipenv
PREFECT_API_URL = http://127.0.0.1:4200/api
MLFLOW_PORT = 5000
PREFECT_PORT = 4200
AWS_REGION = us-east-1
ECR_REPO = milk-pred-test
ECR_URI = 438480637738.dkr.ecr.us-east-1.amazonaws.com/milk-pred-test

# Directories
MLFLOW_DIR = mlflow
IAC_DIR = iac
DEPLOYMENT_DIR = deployment/ondemand/lambda_infra
ORCHESTRATION_DIR = orchestration/flows
TESTS_DIR = tests
DATA_DIR = data/datalake/daily
REPORTS_DIR = reports
LOGS_DIR = logs

# Log files
MLFLOW_LOG = $(LOGS_DIR)/mlflow.log
PREFECT_LOG = $(LOGS_DIR)/prefect.log
MLFLOW_PID = $(LOGS_DIR)/mlflow.pid
PREFECT_PID = $(LOGS_DIR)/prefect.pid

# Colors for output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

.PHONY: help setup start-servers stop-servers start-mlflow start-prefect \
        start-mlflow-fg start-prefect-fg logs-mlflow logs-prefect logs-all \
        run-main-flow run-predictions-flow run-test-flow \
        deploy-infra destroy-infra test-api clean-data \
        test-unit test-all build-docker push-docker \
        status check-resources show-model clean

# Default target
help: ## Show this help
	@echo "$(GREEN)Makefile for MLOps Project - Milk Price Prediction$(NC)"
	@echo ""
	@echo "$(YELLOW)Available targets:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)


start-mlflow: $(LOGS_DIR) ## Start MLflow server in background
	@echo "$(YELLOW)Starting MLflow server...$(NC)"
	@cd $(MLFLOW_DIR) && \
	nohup mlflow server \
		--backend-store-uri=sqlite:///mlflow.db \
		--default-artifact-root=s3://mlflow-models-milk-price-dev \
		--host 0.0.0.0 --port $(MLFLOW_PORT) \
		> ../$(MLFLOW_LOG) 2>&1 & echo $$! > ../$(MLFLOW_PID)
	@echo "$(GREEN)MLflow started on port $(MLFLOW_PORT)$(NC)"
	@echo "$(GREEN)UI available at: http://localhost:$(MLFLOW_PORT)$(NC)"
	@echo "$(YELLOW)View logs with: make logs-mlflow$(NC)"




























## === SERVER MANAGEMENT ===
start-servers: start-mlflow start-prefect ## Start all servers (MLflow and Prefect)
	@echo "$(GREEN)All servers started$(NC)"
	@echo "$(YELLOW)View logs with: make logs-all$(NC)"



start-prefect: $(LOGS_DIR) ## Start Prefect server in background
	@echo "$(YELLOW)Starting Prefect server...$(NC)"
	@nohup prefect server start > $(PREFECT_LOG) 2>&1 & echo $$! > $(PREFECT_PID)
	@sleep 5
	@echo "$(GREEN)Prefect started on port $(PREFECT_PORT)$(NC)"
	@echo "$(GREEN)UI available at: http://localhost:$(PREFECT_PORT)$(NC)"
	@echo "$(YELLOW)View logs with: make logs-prefect$(NC)"

start-mlflow-fg: ## Start MLflow server in foreground (shows logs directly)
	@echo "$(YELLOW)Starting MLflow server in foreground...$(NC)"
	@echo "$(YELLOW)Press Ctrl+C to stop$(NC)"
	@cd $(MLFLOW_DIR) && \
	mlflow server \
		--backend-store-uri=sqlite:///mlflow.db \
		--default-artifact-root=s3://mlflow-models-milk-price-dev \
		--host 0.0.0.0 --port $(MLFLOW_PORT)

start-prefect-fg: ## Start Prefect server in foreground (shows logs directly)
	@echo "$(YELLOW)Starting Prefect server in foreground...$(NC)"
	@echo "$(YELLOW)Press Ctrl+C to stop$(NC)"
	@prefect server start

stop-servers: ## Stop all servers
	@echo "$(YELLOW)Stopping servers...$(NC)"
	@if [ -f $(MLFLOW_PID) ]; then \
		kill `cat $(MLFLOW_PID)` 2>/dev/null || true; \
		rm $(MLFLOW_PID); \
		echo "$(GREEN)MLflow stopped$(NC)"; \
	fi
	@if [ -f $(PREFECT_PID) ]; then \
		kill `cat $(PREFECT_PID)` 2>/dev/null || true; \
		rm $(PREFECT_PID); \
		echo "$(GREEN)Prefect stopped$(NC)"; \
	fi

status: ## Check server status
	@echo "$(YELLOW)Server status:$(NC)"
	@if [ -f $(MLFLOW_PID) ] && kill -0 `cat $(MLFLOW_PID)` 2>/dev/null; then \
		echo "$(GREEN)✓ MLflow running (PID: `cat $(MLFLOW_PID)`)$(NC)"; \
	else \
		echo "$(RED)✗ MLflow not running$(NC)"; \
	fi
	@if [ -f $(PREFECT_PID) ] && kill -0 `cat $(PREFECT_PID)` 2>/dev/null; then \
		echo "$(GREEN)✓ Prefect running (PID: `cat $(PREFECT_PID)`)$(NC)"; \
	else \
		echo "$(RED)✗ Prefect not running$(NC)"; \
	fi





































##################################






## === LOG MANAGEMENT ===
logs-mlflow: ## View MLflow logs in real-time
	@echo "$(YELLOW)MLflow logs (Press Ctrl+C to exit):$(NC)"
	@if [ -f $(MLFLOW_LOG) ]; then \
		tail -f $(MLFLOW_LOG); \
	else \
		echo "$(RED)MLflow log file not found. Is MLflow running?$(NC)"; \
	fi

logs-prefect: ## View Prefect logs in real-time
	@echo "$(YELLOW)Prefect logs (Press Ctrl+C to exit):$(NC)"
	@if [ -f $(PREFECT_LOG) ]; then \
		tail -f $(PREFECT_LOG); \
	else \
		echo "$(RED)Prefect log file not found. Is Prefect running?$(NC)"; \
	fi

logs-all: ## View all logs in real-time (split screen)
	@echo "$(YELLOW)All logs (Press Ctrl+C to exit):$(NC)"
	@if [ -f $(MLFLOW_LOG) ] && [ -f $(PREFECT_LOG) ]; then \
		echo "$(GREEN)=== MLflow Logs ===$(NC)"; \
		tail -n 10 $(MLFLOW_LOG); \
		echo "$(GREEN)=== Prefect Logs ===$(NC)"; \
		tail -n 10 $(PREFECT_LOG); \
		echo "$(YELLOW)Following both logs...$(NC)"; \
		tail -f $(MLFLOW_LOG) $(PREFECT_LOG); \
	else \
		echo "$(RED)Some log files not found. Are the servers running?$(NC)"; \
	fi

logs-show: ## Show recent logs from both servers
	@echo "$(YELLOW)Recent server logs:$(NC)"
	@if [ -f $(MLFLOW_LOG) ]; then \
		echo "$(GREEN)=== MLflow (last 20 lines) ===$(NC)"; \
		tail -n 20 $(MLFLOW_LOG); \
		echo ""; \
	fi
	@if [ -f $(PREFECT_LOG) ]; then \
		echo "$(GREEN)=== Prefect (last 20 lines) ===$(NC)"; \
		tail -n 20 $(PREFECT_LOG); \
	fi

## === FLOW EXECUTION ===
run-main-flow: ## Execute main daily flow
	@echo "$(YELLOW)Running main flow...$(NC)"
	$(PYTHON) $(ORCHESTRATION_DIR)/master_daily_flow.py

run-main-flow-date: ## Execute main flow for specific date (use DATE=YYYY-MM-DD)
	@echo "$(YELLOW)Running main flow for date: $(DATE)$(NC)"
	$(PYTHON) $(ORCHESTRATION_DIR)/master_daily_flow.py $(DATE)

run-predictions-flow: ## Execute daily predictions flow
	@echo "$(YELLOW)Running predictions flow...$(NC)"
	$(PYTHON) $(ORCHESTRATION_DIR)/daily_predictions_flow.py

run-test-flow: ## Execute test ingestion flow
	@echo "$(YELLOW)Running test flow...$(NC)"
	$(PYTHON) $(ORCHESTRATION_DIR)/test_ingest_flow.py

deploy-main-flow: ## Deploy main flow as deployment
	@echo "$(YELLOW)Deploying main flow...$(NC)"
	prefect deployment run 'daily-mlops-pipeline/daily-milk-predictor'

deploy-predictions-flow: ## Deploy predictions flow as deployment
	@echo "$(YELLOW)Deploying predictions flow...$(NC)"
	prefect deployment run 'daily_prediction_flow/daily-milk-predictor'

## === INFRASTRUCTURE MANAGEMENT ===
deploy-infra: ## Deploy infrastructure with Terraform
	@echo "$(YELLOW)Deploying infrastructure...$(NC)"
	@cd $(IAC_DIR) && \
	terraform init && \
	terraform plan && \
	terraform apply -auto-approve
	@echo "$(GREEN)Infrastructure deployed$(NC)"

deploy-infra-hardcoded: ## Deploy hardcoded infrastructure
	@echo "$(YELLOW)Deploying hardcoded infrastructure...$(NC)"
	@cd $(DEPLOYMENT_DIR) && \
	terraform init && \
	terraform plan && \
	terraform apply -auto-approve
	@echo "$(GREEN)Hardcoded infrastructure deployed$(NC)"

destroy-infra: ## Destroy infrastructure
	@echo "$(YELLOW)Destroying infrastructure...$(NC)"
	@cd $(IAC_DIR) && terraform destroy -auto-approve
	@echo "$(GREEN)Infrastructure destroyed$(NC)"

destroy-infra-hardcoded: ## Destroy hardcoded infrastructure
	@echo "$(YELLOW)Destroying hardcoded infrastructure...$(NC)"
	@cd $(DEPLOYMENT_DIR) && terraform destroy -auto-approve
	@echo "$(GREEN)Hardcoded infrastructure destroyed$(NC)"

check-resources: ## Check deployed AWS resources
	@echo "$(YELLOW)Checking AWS resources...$(NC)"
	@cd $(IAC_DIR) && terraform show
	@cd $(DEPLOYMENT_DIR) && terraform show

## === API TESTING ===
test-api: ## Test deployed API (requires API_URL)
	@echo "$(YELLOW)Testing API...$(NC)"
	@if [ -z "$(API_URL)" ]; then \
		echo "$(RED)Error: Specify API_URL. Example: make test-api API_URL=https://xxx.execute-api.us-east-1.amazonaws.com/default$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)First request (may fail due to cold start)...$(NC)"
	@curl -XPOST "$(API_URL)/predict" \
		-H "Content-Type: application/json" \
		-d '{ \
			"Estado": "Jalisco", \
			"Ciudad": "Guadalajara", \
			"Tipo": "Pasteurizada", \
			"Canal": "Autoservicio", \
			"día": 1, \
			"mes": 8, \
			"año": 2025, \
			"dia_semana": "4", \
			"Precio_lag1": 23.5, \
			"Precio_mean7": 23.1 \
		}' || true
	@echo ""
	@echo "$(YELLOW)Second request...$(NC)"
	@curl -XPOST "$(API_URL)/predict" \
		-H "Content-Type: application/json" \
		-d '{ \
			"Estado": "Jalisco", \
			"Ciudad": "Guadalajara", \
			"Tipo": "Pasteurizada", \
			"Canal": "Autoservicio", \
			"día": 1, \
			"mes": 8, \
			"año": 2025, \
			"dia_semana": "4", \
			"Precio_lag1": 23.5, \
			"Precio_mean7": 23.1 \
		}'
	@echo ""

## === DATA MANAGEMENT ===
clean-data: ## Clean data to force reprocessing (requires DATE=YYYY-MM-DD)
	@echo "$(YELLOW)Cleaning data for date: $(DATE)$(NC)"
	@if [ -z "$(DATE)" ]; then \
		echo "$(RED)Error: Specify DATE. Example: make clean-data DATE=2025-08-01$(NC)"; \
		exit 1; \
	fi
	@YEAR=$$(echo $(DATE) | cut -d'-' -f1); \
	MONTH=$$(echo $(DATE) | cut -d'-' -f2); \
	aws s3 rm s3://mlops-milk-datalake/daily/$$YEAR/$$MONTH/$(DATE)-data.parquet || true
	@YEAR=$$(echo $(DATE) | cut -d'-' -f1); \
	MONTH=$$(echo $(DATE) | cut -d'-' -f2); \
	rm -f $(DATA_DIR)/$$YEAR/$$MONTH/$(DATE)-data.parquet || true
	@echo "$(GREEN)Data cleaned for $(DATE)$(NC)"

show-model: ## Show promoted model information
	@echo "$(YELLOW)Promoted model information:$(NC)"
	@aws s3 cp s3://mlflow-models-milk-price-dev/promoted/daily_model.json tmp.json
	@cat tmp.json | python -m json.tool
	@rm tmp.json

show-predictions: ## Show latest generated predictions
	@echo "$(YELLOW)Latest predictions:$(NC)"
	@ls -la $(REPORTS_DIR)/predicciones_*.csv | tail -1 | xargs head -10

## === TESTING ===
test-unit: ## Run unit tests
	@echo "$(YELLOW)Running unit tests...$(NC)"
	pytest $(TESTS_DIR)/unit/ -v

test-unit-file: ## Run specific unit tests (requires FILE)
	@echo "$(YELLOW)Running tests for: $(FILE)$(NC)"
	@if [ -z "$(FILE)" ]; then \
		echo "$(RED)Error: Specify FILE. Example: make test-unit-file FILE=test_check_file_availability.py$(NC)"; \
		exit 1; \
	fi
	pytest $(TESTS_DIR)/unit/$(FILE) -v

test-all: ## Run all tests
	@echo "$(YELLOW)Running all tests...$(NC)"
	pytest $(TESTS_DIR)/ -v

## === DOCKER ===
create-ecr-repo: ## Create ECR repository
	@echo "$(YELLOW)Creating ECR repository...$(NC)"
	aws ecr create-repository --repository-name $(ECR_REPO) --region $(AWS_REGION)

build-docker: ## Build Docker image
	@echo "$(YELLOW)Building Docker image...$(NC)"
	docker build -t $(ECR_REPO) .

push-docker: ## Push image to ECR
	@echo "$(YELLOW)Pushing image to ECR...$(NC)"
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(ECR_URI)
	docker tag $(ECR_REPO):latest $(ECR_URI):latest
	docker push $(ECR_URI):latest

## === CLEANUP ===
clean: ## Clean temporary files and logs
	@echo "$(YELLOW)Cleaning temporary files...$(NC)"
	@rm -f tmp.json
	@rm -rf $(LOGS_DIR)/*.pid
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)Cleanup completed$(NC)"
	@echo "$(YELLOW)Note: Log files preserved in $(LOGS_DIR)/$(NC)"

clean-logs: ## Clean all log files
	@echo "$(YELLOW)Cleaning log files...$(NC)"
	@rm -f $(LOGS_DIR)/*.log
	@echo "$(GREEN)Log files cleaned$(NC)"

## === COMPLETE WORKFLOWS ===
full-setup: setup start-servers ## Complete environment setup
	@echo "$(GREEN)Full setup completed$(NC)"
	@echo "$(YELLOW)View logs with: make logs-all$(NC)"

full-deploy: deploy-infra test-api ## Complete deployment with testing
	@echo "$(GREEN)Full deployment completed$(NC)"

full-test: test-unit run-test-flow ## Run all tests
	@echo "$(GREEN)All tests completed$(NC)"

## === INFORMATION ===
info: ## Show project information
	@echo "$(GREEN)=== PROJECT INFORMATION ===$(NC)"
	@echo "$(YELLOW)Project:$(NC) MLOps - Milk Price Prediction"
	@echo "$(YELLOW)MLflow UI:$(NC) http://localhost:$(MLFLOW_PORT)"
	@echo "$(YELLOW)Prefect UI:$(NC) http://localhost:$(PREFECT_PORT)"
	@echo "$(YELLOW)AWS Region:$(NC) $(AWS_REGION)"
	@echo "$(YELLOW)ECR Repository:$(NC) $(ECR_URI)"
	@echo "$(YELLOW)Logs Directory:$(NC) $(LOGS_DIR)/"
	@echo ""
	@echo "$(YELLOW)Useful commands:$(NC)"
	@echo "  make start-servers    # Start MLflow and Prefect"
	@echo "  make logs-all         # View all logs in real-time"
	@echo "  make run-main-flow    # Execute main flow"
	@echo "  make deploy-infra     # Deploy infrastructure"
	@echo "  make test-api API_URL=<url>  # Test API"
	@echo "  make clean-data DATE=2025-08-01  # Clean data"
