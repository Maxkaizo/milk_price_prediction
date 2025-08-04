# Milk Price Prediction in Mexico 
## MLOps Zoomcamp Capstone

<p align="center">
  <img src="images/banner.png" width="100%" alt="Milk Price Prediction in Mexico" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/language-Python-3776AB" />
  <img src="https://img.shields.io/badge/source%20control-GitHub-181717" />
  <img src="https://img.shields.io/badge/CI/CD-GitHub%20Actions-2088FF" />
  <img src="https://img.shields.io/badge/data%20versioning-DVC-4360F9" />
  <img src="https://img.shields.io/badge/monitoring-Evidently%20AI-8A2BE2" />
  <img src="https://img.shields.io/badge/orchestration-Prefect-0052FF" />
  <img src="https://img.shields.io/badge/api-FastAPI-009688" />
  <img src="https://img.shields.io/badge/containers-Docker-2496ED" />
  <img src="https://img.shields.io/badge/automation-Makefile-FF8C00" />
  <img src="https://img.shields.io/badge/data%20source-SNIIM-0072BC" />
</p>

---

## Project Overview
This project delivers a complete MLOps pipeline to forecast the monthly price of milk in Mexico. It is designed as a production-ready, automated system capable of managing the entire machine learning lifecycle with minimal human intervention.
The core purpose is to move beyond a static model and implement a dynamic solution that automatically adapts to new data. The system achieves this by:
- **Training and versioning models** continuously.
- **Deploying the best model** to a production-ready API.
- **Monitoring** for data drift to ensure prediction quality.
- Automatically **promoting a better-performing model** when available.
- The expected outcome is **a reliable, self-maintaining prediction service** that consistently delivers accurate forecasts, ensuring the most effective model is always active.

---

## Business Context

This project provides a practical forecasting tool for the Mexican milk industry, built on a foundation of reliable, official data.

- **Data Source:** The model is trained using data from Mexico's National System of Information and Market Integration (SNIIM). While the official source updates on Mondays, Wednesdays, and Fridays, our system includes an automated script that checks for new data daily, ensuring our model can always be trained on the most current information available.

- **Business Value:** The system empowers stakeholders—such as producers, distributors, and analysts—to make informed, data-driven decisions. By providing reliable price forecasts, it can help with strategic planning, resource management, and risk mitigation.

- **Deliverables:** The project delivers value through two distinct channels:
      1. An On-Demand Cloud API: A deployed endpoint for real-time price predictions that can be integrated into any application.
      2. A Daily Price Report: A scheduled batch process, orchestrated with Prefect, runs daily to generate and publish a report of suggested prices, providing proactive insights directly to users.

---

## MLOps Context: A Three-Layer Design

Instead of a single, monolithic process, our MLOps approach is designed with a modular, three-layer architecture. This separation of concerns makes the system more robust, scalable, and easier to maintain. This design philosophy sets the stage for the detailed architecture.

- **The Training Layer:** This is a periodic pipeline responsible for creating and versioning our predictive models. It triggers automatically on code or data changes, handling everything from data validation and processing to model training and evaluation. Its main goal is to produce a reliable, version-controlled model candidate.

- **The Inference Layer:** This layer is responsible for delivering predictions to the end-user and operates in two modes:
      1. Online Inference: A cloud-deployed API provides real-time, on-demand predictions.
      2. Batch Inference: A scheduled local process runs daily to generate reports with future price forecasts.

- **The Monitoring Layer:** This is the intelligence of our system. It continuously oversees the entire process, tracking data quality and model performance. It is responsible for detecting issues like data drift and, most importantly, for automatically promoting the best-performing model to production, thus closing the MLOps loop.

---

## Architecture

### Data Preparation - Simulating a Datalake

This layer performs the crucial one-time "bootstrapping" of our data lake. Since the official government data is a single, non-tabular Excel file, it's unsuitable for direct use in a daily pipeline. Our simulate_publication script is executed once to solve this: it processes the entire historical file, converts it into a clean, tabular structure, and partitions the data into daily files stored in AWS S3. This initial setup establishes the structured data lake that the day-to-day training pipelines will interact with, allowing them to simply focus on updating the current day's information.

**Tool Summary:**

| Tool | Role in this Layer |
| :--- | :--- |
| **pandas** | Handles the core logic of reading, cleaning, and restructuring the raw data. |
| **openpyxl** | Enables the initial ingestion of data from the source `.xlsx` file. |
| **AWS S3** | Serves as the data lake where the clean, partitioned data is stored. |
| **boto3 / s3fs** | Provides the Python interface to write the processed files to S3. |

### Development & Training Layer

This is where our models are born and refined. The process begins by fetching the latest prepared data from the S3 data lake. We employ powerful libraries like **scikit-learn** and **XGBoost** to build our predictive models. To ensure peak performance, we automate the search for the best model configuration using **Hyperopt** for hyperparameter tuning. The entire journey, from data ingestion to model evaluation, is orchestrated as a seamless, repeatable pipeline by **Prefect**. Crucially, every experiment's parameters and metrics are logged with **MLflow**, which also serves as our Model Registry to version and store the final model candidates. To maintain code quality, we use **Black** for automated code formatting.

**Tool Summary:**

| Tool | Role in this Layer |
| :--- | :--- |
| **Prefect** | Orchestrates the end-to-end training and evaluation pipeline. |
| **MLflow** | Tracks experiments and manages models in the Model Registry. |
| **scikit-learn / XGBoost** | Core libraries for model training and evaluation. |
| **Hyperopt** | Automates hyperparameter optimization to find the best model. |
| **Black** | Enforces consistent, clean code formatting across the project. |
| **dotenv** | Securely manages credentials and environment variables. |

### Inference & Deployment Layer

Once a model is approved, this layer makes it accessible. The entire cloud infrastructure—including the API Gateway, Lambda functions, and ECR repositories—is managed declaratively using **Terraform**, enabling Infrastructure as a Code (IaC) for consistency and reproducibility. This layer operates in two modes:
1.  **Online Inference:** We use **Flask** and **Gunicorn** to build a robust API, which is containerized with **Docker** and stored in **AWS ECR**. This API is then deployed, often using **AWS Lambda**, and exposed to the world via **AWS API Gateway**.
2.  **Batch Inference:** A separate **Prefect** flow runs on a daily schedule to generate a "Suggested Prices Report". This batch job uses the latest model to make predictions and delivers proactive insights.

**Tool Summary:**

| Tool | Role in this Layer |
| :--- | :--- |
| **Terraform** | Manages and provisions all AWS infrastructure as code (IaC). |
| **Docker** | Containerizes the application for consistent, portable deployment. |
| **Flask / Gunicorn** | Builds and serves the production-ready prediction API. |
| **Prefect** | Orchestrates the scheduled batch inference pipeline for daily reports. |
| **AWS ECR / S3 / Lambda / API Gateway** | The core AWS services for storing artifacts and serving the model. |
| **boto3** | Provides the Python interface to interact with AWS services. |

### Monitoring & Alerting Layer

A deployed model requires constant supervision. This layer acts as the system's watchdog. We use **Evidently AI** to continuously monitor the live model, generating reports that detect data drift and performance degradation. These reports often include visualizations created with **Matplotlib** and **Seaborn**. If a significant event occurs—such as a drop in accuracy or the detection of data drift—the system automatically triggers an alert. These notifications are sent instantly to the team via a **Telegram** bot, enabling a proactive approach to model maintenance.

**Tool Summary:**

| Tool | Role in this Layer |
| :--- | :--- |
| **Evidently AI** | Actively monitors for data drift and model performance issues. |
| **Telegram** | Serves as the notification channel for automated system alerts. |
| **Matplotlib / Seaborn** | Creates visualizations for data analysis and monitoring reports. |

---