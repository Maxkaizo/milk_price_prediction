#!/bin/bash
cd /home/maxkaizo/milk_price_prediction/mlflow

mlflow server \
  --backend-store-uri=sqlite:///mlflow.db \
  --default-artifact-root=s3://mlflow-models-milk-price-dev \
  --host 0.0.0.0 --port 5000
