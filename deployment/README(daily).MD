# 🛠️ Model Deployment - Milk Price Prediction

This document outlines the deployment strategy for the milk price prediction model, using AWS services and containerization.

## 🎯 Deployment Objective

Expose the trained model via a **serverless, real-time prediction service** using AWS Lambda. The Lambda function is containerized (Docker) and will receive input events through **Kinesis Data Streams** or via a REST API (Flask optional fallback).

---

## 📍 Step-by-Step Roadmap

### ✅ Step 0: Manual Prediction Test in Notebook

Before deploying, ensure the model behaves correctly by manually loading it from the MLflow registry and making predictions with test input.

👉 Notebook: [`deployment/test_prediction_in_notebook.ipynb`](./test_prediction_in_notebook.ipynb)

```python
# Example snippet:
from mlflow.pyfunc import load_model

model = load_model("models:/milk-price-predictor/Production")

input_data = {"Estado": "Jalisco", "Ciudad": "Guadalajara", "Tipo": "Pasteurizada", "Canal": "Autoservicio"}
pred = model.predict([input_data])
print(pred)
```

---

### 🐳 Step 1: Containerize the Prediction Service

* Define a lightweight Flask or FastAPI app (optional for REST).
* Install `mlflow`, `scikit-learn`, and the required artifacts inside Docker.
* Use `gunicorn` for efficient serving if needed.

🔧 Dockerfile: [`deployment/docker/Dockerfile`](./docker/Dockerfile)

---

### ☁️ Step 2: Test Locally with Docker

Run locally to confirm the container works and returns valid predictions:

```bash
docker build -t milk-predictor .
docker run -p 9696:9696 milk-predictor
```

Then test using `curl` or Postman.

---

### 🌐 Step 3: Push to AWS ECR

Tag and push the image to your Elastic Container Registry:

```bash
aws ecr get-login-password | docker login ...
docker tag milk-predictor:latest <your-ecr-repo-uri>
docker push <your-ecr-repo-uri>
```

---

### ⚙️ Step 4: Deploy with AWS Lambda

* Create a Lambda function with container image.
* Set environment variables to load artifacts from MLflow or S3.
* Assign permissions to access S3 and Kinesis (if needed).

> You can configure this manually or via Terraform later.

---

### 🔁 Step 5: Connect to AWS Kinesis (Optional)

Set up input/output Kinesis Data Streams:

* Input Stream: JSON data containing feature values.
* Output Stream: JSON result with predicted price.

Configure your Lambda to be triggered by the input stream.

---

### 🧪 Step 6: Trigger and Validate

Send test payloads to the Lambda endpoint or via the stream.

---

### 🧱 Step 7: Automate Infrastructure with Terraform (Next)

Move all AWS resource definitions to Terraform.

```bash
cd deployment/terraform/
terraform init
terraform apply
```

---

### 🗓️ Planned Enhancements

* Add authentication to REST service (if enabled).
* Add schema validation.
* Schedule batch predictions via Prefect or Lambda cron.
* Integrate monitoring (data drift alerts already done).

---

## 📎 References

* MLflow Model: `models:/milk-price-predictor/Production`
* Registry: [MLflow UI](http://localhost:5000/#/models)
* Sample data: `data/processed/`
