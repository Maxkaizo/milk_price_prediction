# Terraform main.tf for Milk Price Prediction Project

terraform {
  required_version = ">= 1.0"
  backend "s3" {
    bucket  = "mlops-milk-tf-state"
    key     = "milk-pipeline.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current_identity" {}

locals {
  account_id = data.aws_caller_identity.current_identity.account_id
}

# Input event stream (milk events)
module "source_kinesis_stream" {
  source              = "./modules/kinesis"
  retention_period    = 48
  shard_count         = 2
  stream_name         = "${var.source_stream_name}-${var.project_id}"
  shard_level_metrics = []
  tags                = var.project_id
}

# Output prediction stream
module "output_kinesis_stream" {
  source              = "./modules/kinesis"
  retention_period    = 48
  shard_count         = 2
  stream_name         = "${var.output_stream_name}-${var.project_id}"
  shard_level_metrics = []
  tags                = var.project_id
}

# S3 bucket to store ML model
module "s3_bucket" {
  source      = "./modules/s3"
  bucket_name = "${var.model_bucket}-${var.project_id}"
  project_id  = var.project_id
}

# ECR registry and image push
module "ecr_image" {
  source                      = "./modules/ecr"
  ecr_repo_name               = "${var.ecr_repo_name}-${var.project_id}"
  account_id                  = local.account_id
  region                      = var.aws_region
  lambda_function_local_path = var.lambda_function_local_path
  docker_image_local_path     = var.docker_image_local_path
  ecr_image_tag               = "latest"
}

# IAM role and permissions for Lambda
module "iam_lambda" {
  source               = "./modules/iam"
  lambda_function_name = "${var.lambda_function_name}-${var.project_id}"
  output_stream_arn    = module.output_kinesis_stream.stream_arn
  source_stream_arn    = module.source_kinesis_stream.stream_arn
  model_bucket         = module.s3_bucket.name
}

# Lambda function
module "lambda_function" {
  source                     = "./modules/lambda"
  image_uri                  = module.ecr_image.image_uri
  lambda_function_name       = "${var.lambda_function_name}-${var.project_id}"
  model_bucket               = module.s3_bucket.name
  output_stream_name         = "${var.output_stream_name}-${var.project_id}"
  source_stream_arn          = module.source_kinesis_stream.stream_arn
  lambda_role_arn            = module.iam_lambda.lambda_role_arn
  kinesis_mapping_dependency = module.iam_lambda
}

# CI/CD outputs
output "lambda_function" {
  value = "${var.lambda_function_name}-${var.project_id}"
}

output "model_bucket" {
  value = module.s3_bucket.name
}

output "predictions_stream_name" {
  value = "${var.output_stream_name}-${var.project_id}"
}

output "ecr_repo" {
  value = "${var.ecr_repo_name}-${var.project_id}"
}
