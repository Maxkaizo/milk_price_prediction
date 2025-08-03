project_id      = "leche-stg"

repository_name = "lambda-repo"
lambda_name     = "milk-api"
api_name        = "milk-api"

aws_region      = "us-east-1"

s3_resources = [
  "arn:aws:s3:::mlflow-models-milk-price-dev/*"
]

lambda_timeout  = 60
lambda_memory   = 3008
route_key       = "POST /predict"
stage_name      = "default"
