# Milk Price Prediction in Mexico – MLOps Zoomcamp Capstone

![alt text](images/banner.png)


## 1. Project Overview
This project delivers a complete MLOps pipeline to forecast the monthly price of milk in Mexico. It is designed as a production-ready, automated system capable of managing the entire machine learning lifecycle with minimal human intervention.
The core purpose is to move beyond a static model and implement a dynamic solution that automatically adapts to new data. The system achieves this by:
- **Training and versioning models** continuously.
- **Deploying the best model** to a production-ready API.
- **Monitoring** for data drift to ensure prediction quality.
- Automatically **promoting a better-performing model** when available.
- The expected outcome is **a reliable, self-maintaining prediction service** that consistently delivers accurate forecasts, ensuring the most effective model is always active.

## 3. Business Context

This project provides a practical forecasting tool for the Mexican milk industry, built on a foundation of reliable, official data.

- **Data Source:** The model is trained using data from Mexico's National System of Information and Market Integration (SNIIM). While the official source updates on Mondays, Wednesdays, and Fridays, our system includes an automated script that checks for new data daily, ensuring our model can always be trained on the most current information available.

- **Business Value:** The system empowers stakeholders—such as producers, distributors, and analysts—to make informed, data-driven decisions. By providing reliable price forecasts, it can help with strategic planning, resource management, and risk mitigation.

- **Deliverables:** The project delivers value through two distinct channels:
> 1. An On-Demand Cloud API: A deployed endpoint for real-time price predictions that can be integrated into any application.
> 2. A Daily Price Report: A scheduled batch process, orchestrated with Prefect, runs daily to generate and publish a report of suggested prices, providing proactive insights directly to users.

## 4. MLOps Context: A Three-Layer Design

Instead of a single, monolithic process, our MLOps approach is designed with a modular, three-layer architecture. This separation of concerns makes the system more robust, scalable, and easier to maintain. This design philosophy sets the stage for the detailed architecture.

- **The Training Layer:** This is a periodic pipeline responsible for creating and versioning our predictive models. It triggers automatically on code or data changes, handling everything from data validation and processing to model training and evaluation. Its main goal is to produce a reliable, version-controlled model candidate.

- **The Inference Layer:** This layer is responsible for delivering predictions to the end-user and operates in two modes:
> 1. Online Inference: A cloud-deployed API provides real-time, on-demand predictions.
> 2. Batch Inference: A scheduled local process runs daily to generate reports with future price forecasts.

- **The Monitoring Layer:** This is the intelligence of our system. It continuously oversees the entire process, tracking data quality and model performance. It is responsible for detecting issues like data drift and, most importantly, for automatically promoting the best-performing model to production, thus closing the MLOps loop.






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




