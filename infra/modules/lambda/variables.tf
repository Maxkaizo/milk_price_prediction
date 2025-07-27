variable "lambda_function_name" {
  description = "Name of the Lambda function"
  type        = string
}

variable "image_uri" {
  description = "URI of the Docker image in ECR"
  type        = string
}

variable "lambda_role_arn" {
  description = "ARN of the IAM role assigned to the Lambda function"
  type        = string
}

variable "output_stream_name" {
  description = "Name of the Kinesis output stream (for prediction output)"
  type        = string
}

variable "model_bucket" {
  description = "Name of the S3 bucket where the model is stored"
  type        = string
}

variable "source_stream_arn" {
  description = "ARN of the Kinesis input stream (event source)"
  type        = string
}

variable "kinesis_mapping_dependency" {
  description = "Dependency for event source mapping (e.g., IAM policy attachment)"
  type        = any
}
