project_id      = "prod-milk-pred"

repository_name = "prod-lambda-repo"
lambda_name     = "prod-milk-lambda"
api_name        = "prod-milk-api"

aws_region      = "us-east-1"

s3_resources = [
  "arn:aws:s3:::mlflow-models-milk-price-dev/*"
]

lambda_timeout  = 60
lambda_memory   = 3008
route_key       = "POST /predict"
stage_name      = "default"
