# MLOps Project - Milk Price Prediction
## Complete Setup and Execution Guide

This guide provides two approaches for each step: **automated with Makefile** and **manual with direct commands**. Choose the approach that best fits your needs or use both for validation and troubleshooting.

---

## 📋 Prerequisites

To run this project end-to-end, ensure you have the following set up:

-   **Python 3.12+** with `pipenv` installed.
-   **AWS CLI** configured with appropriate credentials.
    - **Note on credentials**: Our development and testing were performed using the standard AWS configuration file at `~/.aws/credentials`. However, the setup should also work correctly with credentials configured as environment variables.
    - **Sufficient AWS Permissions**: The AWS credentials used must be associated with an IAM policy that allows creating and modifying resources for ECR, Lambda, API Gateway, S3, and IAM.
-   **Docker** (for containerization steps).
-   **Terraform** (for infrastructure deployment).
-   **Telegram Bot Token and Chat ID (Optional)**: For notifications to work, you need to set up a `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` as Prefect secrets. The flows will run without them, but no alerts will be sent.
-   **Access to S3 buckets**: `mlops-milk-datalake` and `mlflow-models-milk-price-dev`.
    -   The project uses hardcoded bucket names to enforce a clear separation between the data lake (raw and processed data) and MLflow's model artifacts.

    If these buckets do not exist, you can create them using the following AWS CLI commands:
    ```bash
    # Create the datalake bucket
    aws s3api create-bucket --bucket mlops-milk-datalake --region us-east-1

    # Create the MLflow models bucket
    aws s3api create-bucket --bucket mlflow-models-milk-price-dev --region us-east-1
    ```

---

## 🚀 Quick Start (Automated)

```bash
# Complete setup and start
make full-setup
make info
```

---

## 📖 Step-by-Step Guide

### 1. Initial Environment Setup

#### 🤖 **With Makefile:**
```bash
make setup
```

#### 🔧 **Direct Commands:**
```bash
# Install dependencies
pipenv install

# Activate virtual environment
pipenv shell

# Configure Prefect
prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api

# Create logs directory
mkdir -p logs
```

**✅ Validation:**
```bash
# Check Python environment
which python
pip list | grep -E "(prefect|mlflow|pandas)"

# Check Prefect configuration
prefect config view
```

---

### 2. Start MLflow Server

#### 🤖 **With Makefile:**
```bash
# Background mode (recommended)
make start-mlflow

# Foreground mode (for debugging)
make start-mlflow-fg
```

#### 🔧 **Direct Commands:**
```bash
# Background mode
cd mlflow
nohup mlflow server \
  --backend-store-uri=sqlite:///mlflow.db \
  --default-artifact-root=s3://mlflow-models-milk-price-dev \
  --host 0.0.0.0 --port 5000 \
  > ../logs/mlflow.log 2>&1 & echo $! > ../logs/mlflow.pid

# Foreground mode (for debugging)
cd mlflow
mlflow server \
  --backend-store-uri=sqlite:///mlflow.db \
  --default-artifact-root=s3://mlflow-models-milk-price-dev \
  --host 0.0.0.0 --port 5000
```

**✅ Validation:**
```bash
# Check if MLflow is running
curl -s http://localhost:5000/health || echo "MLflow not responding"

# View logs
tail -f logs/mlflow.log

# Check process
ps aux | grep mlflow
```

---

### 3. Start Prefect Server

#### 🤖 **With Makefile:**
```bash
# Background mode (recommended)
make start-prefect

# Foreground mode (for debugging)
make start-prefect-fg
```

#### 🔧 **Direct Commands:**
```bash
# Background mode
nohup prefect server start > logs/prefect.log 2>&1 & echo $! > logs/prefect.pid
sleep 5

# Foreground mode (for debugging)
prefect server start
```

**✅ Validation:**
```bash
# Check if Prefect is running
curl -s http://localhost:4200/api/health || echo "Prefect not responding"

# View logs
tail -f logs/prefect.log

# Check Prefect status
prefect server status
```

---

### 4. Check Server Status

#### 🤖 **With Makefile:**
```bash
make status
```

#### 🔧 **Direct Commands:**
```bash
echo "=== Server Status ==="

# Check MLflow
if [ -f logs/mlflow.pid ] && kill -0 `cat logs/mlflow.pid` 2>/dev/null; then
    echo "✓ MLflow running (PID: `cat logs/mlflow.pid`)"
else
    echo "✗ MLflow not running"
fi

# Check Prefect
if [ -f logs/prefect.pid ] && kill -0 `cat logs/prefect.pid` 2>/dev/null; then
    echo "✓ Prefect running (PID: `cat logs/prefect.pid`)"
else
    echo "✗ Prefect not running"
fi

# Check ports
netstat -tlnp | grep -E ":(5000|4200)"
```

**🌐 Access URLs:**
- MLflow UI: http://localhost:5000
- Prefect UI: http://localhost:4200

---

### 5. Execute Main Data Flow

#### 🤖 **With Makefile:**
```bash
# For current date
make run-main-flow

# For specific date
make run-main-flow-date DATE=2025-08-01
```

#### 🔧 **Direct Commands:**
```bash
# For current date
python orchestration/flows/master_daily_flow.py

# For specific date
python orchestration/flows/master_daily_flow.py 2025-08-01
```

**✅ Validation:**
```bash
# Check flow execution in Prefect UI
# Or check recent flow runs
prefect flow-run ls --limit 5

# Check if new data was processed
ls -la data/datalake/daily/$(date +%Y)/$(date +%m)/

# Check S3 for new files
aws s3 ls s3://mlops-milk-datalake/daily/$(date +%Y)/$(date +%m)/
```

---

### 6. Generate Daily Predictions

#### 🤖 **With Makefile:**
```bash
make run-predictions-flow
```

#### 🔧 **Direct Commands:**
```bash
python orchestration/flows/daily_predictions_flow.py
```

**✅ Validation:**
```bash
# Check generated predictions
ls -la reports/predicciones_*.csv | tail -5

# View sample predictions
head -10 reports/predicciones_$(date +%Y-%m-%d).csv

# Check S3 upload
aws s3 ls s3://mlops-milk-datalake/predicciones/$(date +%Y-%m-%d)/
```

---

### 7. View Model Information

#### 🤖 **With Makefile:**
```bash
make show-model
```

#### 🔧 **Direct Commands:**
```bash
# Download and view promoted model info
aws s3 cp s3://mlflow-models-milk-price-dev/promoted/daily_model.json tmp.json
cat tmp.json | python -m json.tool
rm tmp.json
```

**✅ Expected Output:**
```json
{
  "model_name": "milk-price-predictor-rf",
  "version": "5",
  "run_id": "276aa9b997564336a112a62a295caae4",
  "artifact_uri": "models:/m-341d8b0ad65c4334a6132ab6f0bb7a40",
  "rmse": 0.2294937078293053,
  "promoted_stage": "Staging",
  "promotion_time": "2025-08-03T19:46:23.117576"
}
```

---

### 8. Deploy Infrastructure

#### 🤖 **With Makefile:**
```bash
# Main infrastructure
make deploy-infra

# Or hardcoded version
make deploy-infra-hardcoded
```

#### 🔧 **Direct Commands:**
```bash
# Main infrastructure
cd iac
terraform init
terraform plan
terraform apply -auto-approve

# Or hardcoded version
cd deployment/ondemand/lambda_infra
terraform init
terraform plan
terraform apply -auto-approve
```

**✅ Validation:**
```bash
# Check deployed resources
cd iac && terraform show
# Or: cd deployment/ondemand/lambda_infra && terraform show

# Note the API URL from output
# Example: api_url = "https://28lp654o4e.execute-api.us-east-1.amazonaws.com/default"
```

---

### 9. Test Deployed API

#### 🤖 **With Makefile:**
```bash
# Replace with your actual API URL from Terraform output
make test-api API_URL=https://28lp654o4e.execute-api.us-east-1.amazonaws.com/default
```

#### 🔧 **Direct Commands:**
```bash
# Replace with your actual API URL
API_URL="https://28lp654o4e.execute-api.us-east-1.amazonaws.com/default"

echo "First request (may fail due to cold start)..."
curl -XPOST "${API_URL}/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "Estado": "Jalisco",
    "Ciudad": "Guadalajara",
    "Tipo": "Pasteurizada",
    "Canal": "Autoservicio",
    "día": 1,
    "mes": 8,
    "año": 2025,
    "dia_semana": "4",
    "Precio_lag1": 23.5,
    "Precio_mean7": 23.1
  }' || true

echo -e "\n\nSecond request..."
curl -XPOST "${API_URL}/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "Estado": "Jalisco",
    "Ciudad": "Guadalajara",
    "Tipo": "Pasteurizada",
    "Canal": "Autoservicio",
    "día": 1,
    "mes": 8,
    "año": 2025,
    "dia_semana": "4",
    "Precio_lag1": 23.5,
    "Precio_mean7": 23.1
  }'
```

**✅ Expected Response:**
```json
{"predicted_price": 23.311434689771172}
```

---

### 10. Run Tests

#### 🤖 **With Makefile:**
```bash
# All unit tests
make test-unit

# Specific test file
make test-unit-file FILE=test_check_file_availability.py

# All tests
make test-all
```

#### 🔧 **Direct Commands:**
```bash
# All unit tests
pytest tests/unit/ -v

# Specific test file
pytest tests/unit/test_check_file_availability.py -v

# All tests
pytest tests/ -v
```

**✅ Validation:**
```bash
# Check test results
echo "Test results should show PASSED status"
```

---


## 🔧 Data Management

### Clean Data for Reprocessing

#### 🤖 **With Makefile:**
```bash
make clean-data DATE=2025-08-01
```

#### 🔧 **Direct Commands:**
```bash
DATE="2025-08-01"
YEAR=$(echo $DATE | cut -d'-' -f1)
MONTH=$(echo $DATE | cut -d'-' -f2)

# Remove from S3
aws s3 rm s3://mlops-milk-datalake/daily/$YEAR/$MONTH/$DATE-data.parquet || true

# Remove local file
rm -f data/datalake/daily/$YEAR/$MONTH/$DATE-data.parquet || true

echo "Data cleaned for $DATE"
```

**✅ Validation:**
```bash
# Verify files are removed
DATE="2025-08-01"
YEAR=$(echo $DATE | cut -d'-' -f1)
MONTH=$(echo $DATE | cut -d'-' -f2)

aws s3 ls s3://mlops-milk-datalake/daily/$YEAR/$MONTH/ | grep $DATE || echo "S3 file removed"
ls data/datalake/daily/$YEAR/$MONTH/ | grep $DATE || echo "Local file removed"
```

---

## 📊 Log Management

### View Logs in Real-Time

#### 🤖 **With Makefile:**
```bash
# View all logs
make logs-all

# View MLflow logs only
make logs-mlflow

# View Prefect logs only
make logs-prefect

# Show recent logs (last 20 lines)
make logs-show
```

#### 🔧 **Direct Commands:**
```bash
# View all logs
echo "=== MLflow Logs ==="
tail -n 10 logs/mlflow.log
echo -e "\n=== Prefect Logs ==="
tail -n 10 logs/prefect.log
echo -e "\nFollowing both logs..."
tail -f logs/mlflow.log logs/prefect.log

# View MLflow logs only
tail -f logs/mlflow.log

# View Prefect logs only
tail -f logs/prefect.log

# Show recent logs
echo "=== MLflow (last 20 lines) ==="
tail -n 20 logs/mlflow.log
echo -e "\n=== Prefect (last 20 lines) ==="
tail -n 20 logs/prefect.log
```

---

## 🧹 Cleanup Operations

### Stop Servers

#### 🤖 **With Makefile:**
```bash
make stop-servers
```

#### 🔧 **Direct Commands:**
```bash
# Stop MLflow
if [ -f logs/mlflow.pid ]; then
    kill `cat logs/mlflow.pid` 2>/dev/null || true
    rm logs/mlflow.pid
    echo "MLflow stopped"
fi

# Stop Prefect
if [ -f logs/prefect.pid ]; then
    kill `cat logs/prefect.pid` 2>/dev/null || true
    rm logs/prefect.pid
    echo "Prefect stopped"
fi
```

### Clean Temporary Files

#### 🤖 **With Makefile:**
```bash
# Clean temp files (preserves logs)
make clean

# Clean logs too
make clean-logs
```

#### 🔧 **Direct Commands:**
```bash
# Clean temp files (preserves logs)
rm -f tmp.json
rm -rf logs/*.pid
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Clean logs
rm -f logs/*.log
```

### Destroy Infrastructure

#### 🤖 **With Makefile:**
```bash
# Destroy main infrastructure
make destroy-infra

# Destroy hardcoded infrastructure
make destroy-infra-hardcoded
```

#### 🔧 **Direct Commands:**
```bash
# Destroy main infrastructure
cd iac
terraform destroy -auto-approve

# Destroy hardcoded infrastructure
cd deployment/ondemand/lambda_infra
terraform destroy -auto-approve
```

---

## 🔄 Complete Workflows

### Development Workflow

#### 🤖 **With Makefile:**
```bash
# 1. Setup and start
make full-setup

# 2. Run daily pipeline
make run-main-flow

# 3. Generate predictions
make run-predictions-flow

# 4. Check results
make show-model
make show-predictions

# 5. View logs if needed
make logs-show
```

#### 🔧 **Direct Commands:**
```bash
# 1. Setup and start
pipenv install && pipenv shell
prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
mkdir -p logs

# Start servers
cd mlflow && nohup mlflow server --backend-store-uri=sqlite:///mlflow.db --default-artifact-root=s3://mlflow-models-milk-price-dev --host 0.0.0.0 --port 5000 > ../logs/mlflow.log 2>&1 & echo $! > ../logs/mlflow.pid
cd ..
nohup prefect server start > logs/prefect.log 2>&1 & echo $! > logs/prefect.pid

# 2. Run daily pipeline
python orchestration/flows/master_daily_flow.py

# 3. Generate predictions
python orchestration/flows/daily_predictions_flow.py

# 4. Check results
aws s3 cp s3://mlflow-models-milk-price-dev/promoted/daily_model.json tmp.json && cat tmp.json | python -m json.tool && rm tmp.json
ls -la reports/predicciones_*.csv | tail -1 | xargs head -10

# 5. View logs if needed
tail -n 20 logs/mlflow.log logs/prefect.log
```

### Production Deployment Workflow

#### 🤖 **With Makefile:**
```bash
# 1. Setup environment
make full-setup

# 2. Run tests
make test-unit

# 3. Deploy infrastructure
make deploy-infra

# 4. Test API (use URL from Terraform output)
make test-api API_URL=https://your-api-url.com/default

# 5. Cleanup when done
make destroy-infra
make stop-servers
```

#### 🔧 **Direct Commands:**
```bash
# 1. Setup environment
pipenv install && pipenv shell
mkdir -p logs
# ... (start servers as shown above)

# 2. Run tests
pytest tests/unit/ -v

# 3. Deploy infrastructure
cd iac
terraform init && terraform plan && terraform apply -auto-approve
cd ..

# 4. Test API (replace with actual URL)
API_URL="https://your-api-url.com/default"
curl -XPOST "${API_URL}/predict" -H "Content-Type: application/json" -d '{"Estado": "Jalisco", "Ciudad": "Guadalajara", "Tipo": "Pasteurizada", "Canal": "Autoservicio", "día": 1, "mes": 8, "año": 2025, "dia_semana": "4", "Precio_lag1": 23.5, "Precio_mean7": 23.1}'

# 5. Cleanup when done
cd iac && terraform destroy -auto-approve && cd ..
kill `cat logs/mlflow.pid` `cat logs/prefect.pid` 2>/dev/null || true
rm logs/*.pid
```

---

## 🚨 Troubleshooting

### Common Issues and Solutions

#### Servers Won't Start

**Problem:** Ports already in use
```bash
# Check what's using the ports
netstat -tlnp | grep -E ":(5000|4200)"

# Kill processes if needed
sudo lsof -ti:5000 | xargs kill -9
sudo lsof -ti:4200 | xargs kill -9
```

**Problem:** Permission issues
```bash
# Check file permissions
ls -la logs/
chmod 755 logs/
```

#### AWS Issues

**Problem:** Credentials not configured
```bash
# Check AWS credentials
aws sts get-caller-identity

# Configure if needed
aws configure
```

**Problem:** S3 access denied
```bash
# Test S3 access
aws s3 ls s3://mlops-milk-datalake/
aws s3 ls s3://mlflow-models-milk-price-dev/

# Check IAM permissions for S3 access
```

#### API Issues

**Problem:** Lambda cold start failures
- **Solution:** Always try the API call twice
- First call may fail with "Service Unavailable"
- Second call should work

**Problem:** Model not found
```bash
# Check if model is promoted
aws s3 ls s3://mlflow-models-milk-price-dev/promoted/

# Check MLflow UI for model status
# Visit: http://localhost:5000
```

#### Flow Execution Issues

**Problem:** Prefect flows fail
```bash
# Check Prefect server status
prefect server status

# Check flow runs in UI
# Visit: http://localhost:4200

# Check logs
tail -f logs/prefect.log
```

**Problem:** Data files not found
```bash
# Check if data exists
aws s3 ls s3://mlops-milk-datalake/daily/$(date +%Y)/$(date +%m)/

# Clean and retry if needed
make clean-data DATE=$(date +%Y-%m-%d)
make run-main-flow
```

---

## 📚 Quick Reference

### Essential Commands

| Task | Makefile | Direct Command |
|------|----------|----------------|
| Start all servers | `make start-servers` | See "Start MLflow/Prefect" sections |
| Check status | `make status` | `ps aux \| grep -E "(mlflow\|prefect)"` |
| View logs | `make logs-all` | `tail -f logs/*.log` |
| Run main flow | `make run-main-flow` | `python orchestration/flows/master_daily_flow.py` |
| Deploy infra | `make deploy-infra` | `cd iac && terraform apply` |
| Test API | `make test-api API_URL=<url>` | `curl -XPOST "<url>/predict" ...` |
| Stop servers | `make stop-servers` | `kill $(cat logs/*.pid)` |
| Clean up | `make clean` | `rm -f logs/*.pid tmp.json` |

### File Locations

- **Logs:** `logs/mlflow.log`, `logs/prefect.log`
- **PIDs:** `logs/mlflow.pid`, `logs/prefect.pid`
- **Data:** `data/datalake/daily/YYYY/MM/`
- **Reports:** `reports/predicciones_YYYY-MM-DD.csv`
- **Infrastructure:** `iac/` (main), `deployment/ondemand/lambda_infra/` (hardcoded)

### URLs

- **MLflow UI:** http://localhost:5000
- **Prefect UI:** http://localhost:4200
- **API URL:** Provided by Terraform output after deployment

---

## 🎯 Next Steps

1. **Choose your approach:** Use Makefile for automation or direct commands for learning/debugging
2. **Start with development workflow** to understand the process
3. **Move to production deployment** when ready
4. **Use troubleshooting section** when issues arise
5. **Customize the Makefile** to fit your specific needs

Remember: Both approaches achieve the same result. Use Makefile for efficiency, direct commands for understanding and troubleshooting!

