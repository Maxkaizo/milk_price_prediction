## 🥛 Milk Price Prediction in Mexico – MLOps Zoomcamp Capstone

### Project Overview
This project simulates a fully operational MLOps pipeline for **daily milk price prediction in Mexico**, developed as part of the [MLOps Zoomcamp](https://github.com/DataTalksClub/mlops-zoomcamp) final project.

The primary objective is to **recreate a realistic MLOps environment** rather than focus on model accuracy. The emphasis is on automation, reproducibility, monitoring, and infrastructure management.

Still, the use case has **real-world business relevance**: milk prices in Mexico show wide variation across states and even between cities in the same state. A pipeline like this could support **data-driven pricing strategies**, **supply chain decisions**, and **regional analysis**.

---

### Business Motivation
Milk is a high-consumption staple product. Prices fluctuate significantly due to transportation, distribution, and local economic factors. For instance:

- Pasteurized milk in **northern cities** may cost up to **40% more** than in southern states.
- Daily shifts are common based on logistics and retailer conditions.

A system like this could benefit companies, cooperatives, or regulators by:

- Anticipating price variations  
- Supporting transparent pricing strategies  
- Identifying market opportunities or pricing anomalies  
- Enabling regional demand forecasting

---

### MLOps Scope
This project implements the complete MLOps lifecycle across **three solution layers**:

#### 1. Training Layer (Local)
- Implemented **locally to reduce cloud cost**.
- Ingests and preprocesses daily data from SNIIM (Excel to Parquet).
- Uses **Prefect 3.x** for orchestration of training pipelines.
- Trains **XGBoost models** using **Hyperopt** for hyperparameter tuning.
- Tracks all trials and model artifacts with **MLflow**, including metrics and parameters.
- Trained models are saved and versioned in a **remote S3 bucket**.

#### 2. Inference Layer (Cloud)
- Deployed on **AWS** using **Terraform** for Infrastructure-as-Code.
- Two modes of prediction:
  - **Online inference**: An **AWS Lambda function** (containerized via Docker in ECR), exposed via **API Gateway** for real-time requests.
  - **Batch inference**: A scheduled process that generates **daily prediction reports** (initially run locally, with plans to move to cloud).

#### 3. Monitoring Layer (Hybrid)
- **Model drift detection** using [Evidently AI](https://evidentlyai.com/) over recent vs historical performance.
- Sends **alerts via Telegram** when drift exceeds defined thresholds.
- Future plan: integrate with **Grafana dashboards** to monitor service uptime (API health check) and model behavior.

---

### Cloud Infrastructure
- Cloud services are provisioned using **Terraform**.
- Includes:
  - S3 buckets for data lake and model artifacts  
  - ECR for Docker containers  
  - Lambda + API Gateway for real-time inference  
  - IAM roles and logging resources  
- Upcoming: Grafana and CloudWatch integration for service monitoring.

---

### Rubric Alignment (MLOps Zoomcamp)

| Criterion                    | Status                                                                 |
|-----------------------------|-------------------------------------------------------------------------|
| **Problem description**     | Clear and well described with business context                         |
| **Cloud**                   | AWS used with Terraform for IaC                                        |
| **Experiment tracking**     | MLflow used for tracking + model registry, including Hyperopt trials   |
| **Workflow orchestration**  | Fully deployed with Prefect flows                                      |
| **Model deployment**        | Deployed to AWS Lambda via Docker + ECR                                |
| **Model monitoring**        | Drift detection with alerts + future Grafana health checks             |
| **Reproducibility**         | All code parameterized, structured, and documented                     |
| **Best practices**          | *(To be added)* CI/CD, linter, Makefile, pre-commit hooks planned      |

---

### Next Steps
- Finalize CI/CD with GitHub Actions  
- Add integration test + automated drift dashboard  
- Move batch predictions to AWS Step Functions or ECS




