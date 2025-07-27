# AWS region where resources will be created
variable "aws_region" {
  description = "AWS region to create resources"
  default     = "us-east-1"
}

# Project identifier (used for naming and tagging resources)
variable "project_id" {
  description = "Project identifier"
  default     = "mlops-zoomcamp"
}

# Name of the input Kinesis stream (source of data)
variable "source_stream_name" {
  description = "Name of the input Kinesis stream"
}

# Name of the output Kinesis stream (predictions)
variable "output_stream_name" {
  description = "Name of the output Kinesis stream"
}

# S3 bucket where the ML model is stored
variable "model_bucket" {
  description = "S3 bucket name containing the trained model"
}

# Local path to the Lambda function code (ZIP file or folder)
variable "lambda_function_local_path" {
  description = "Local path to the Lambda function code"
}

# Local path to the Docker image for Lambda (if using container deployment)
variable "docker_image_local_path" {
  description = "Local path to the Docker image build context"
}

# Name of the ECR repository to push the Docker image
variable "ecr_repo_name" {
  description = "ECR repository name for container image"
}

# Name of the Lambda function
variable "lambda_function_name" {
  description = "Name of the Lambda function"
}
