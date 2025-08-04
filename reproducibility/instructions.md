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
-   **Cloned Repository:** to have all files and prepared structure. 
```bash
# clone repo
git clone git@github.com:Maxkaizo/milk_price_prediction.git

# switch to root folder
cd milk_price_prediction
```
-   **Environment and Dependencies:** Documented in Pipfile, you can also intall and enable them with this commands:
```bash
# Install dependencies
pipenv install

# Activate virtual environment
pipenv shell
```

**🌐 Access URLs:**
- MLflow UI: http://localhost:5000
- Prefect UI: http://localhost:4200


### Start MLflow Server

**With Makefile:**
```bash
# Background mode
make start-mlflow
```

**Direct Commands:**
```bash
# Background mode
cd mlflow
nohup mlflow server \
  --backend-store-uri=sqlite:///mlflow.db \
  --default-artifact-root=s3://mlflow-models-milk-price-dev \
  --host 0.0.0.0 --port 5000 \
  > ../logs/mlflow.log 2>&1 &
ps -ef | grep mlflow  | head -n 2 | tail -n 1 | cut -d" " -f 4 > ../logs/mlflow.pid

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
### Stop MLflow Server

**With Makefile:**
```bash
# Background mode
make stop-mlflow
```

**With Direct Commands:**
```bash
# using logged pid
kill $(cat logs/mlflow.pid)

# or directly
kill $(ps -ef | grep mlflow  | head -n 2 | tail -n 1 | cut -d" " -f 4)
```

### Start Prefect Server

**With Makefile:**
```bash
# Background mode
make start-prefect
```

**Direct Commands:**
```bash
# Background mode
prefect server start --background
```

**✅ Validation:**
```bash
# Check if Prefect is running
curl -s http://localhost:4200/api/health || echo "Prefect not responding"
```

### Stop Prefect Server

**With Makefile:**
```bash
# Background mode
make stop-prefect
```

**With Direct Commands:**
```bash
# directly
prefect server stop
```

### Deploy and Run Prefect flows

- `master_daily_flow.py` is the main flow to check for new data, run a trining process, select and promote the best resulting model
- It's scheduled to run on a daily basis at 1 pm 
- It can also be launched mannualy
- If there's no new file, a confirmation message is received via Telegram
- IF there's a new file, all the flow runs and it sends confirmations of each step via Telegram

```bash
# deploy the flow
python orchestration/flows/master_daily_flow.py &

# To manualy launch a run you can also do:
prefect deployment run 'daily-mlops-pipeline/daily-milk-predictor'
```
- For testing purposes we can force the proces by using a past date and deleting files in the datalake (local backup and s3 bucket), for example

```bash
# delete file on s3
aws s3 rm s3://mlops-milk-datalake/daily/2025/08/2025-08-01-data.parquet

# delete files locally
rm data/datalake/daily/2025/08/2025-08-01-data.parquet

# Force the run using custom date
prefect deployment run 'daily-mlops-pipeline/daily-milk-predictor' \
  --param execution_date="2025-08-01"
```

- `generate_daily_predictions.py` is a batch flow and it runs price predictions for all variations of State, City, and Product

- It can also be launched mannualy


```bash
# deploy the flow
python orchestration/flows/daily_predictions_flow.py &

# To manualy launch a run you can also do:
prefect deployment run 'daily_prediction_flow/daily-milk-predictor' &
```



