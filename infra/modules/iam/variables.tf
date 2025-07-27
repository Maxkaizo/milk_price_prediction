variable "lambda_function_name" {
  description = "Name of the Lambda function"
  type        = string
}

variable "output_stream_arn" {
  description = "ARN of the output Kinesis stream"
  type        = string
}

variable "model_bucket" {
  description = "Name of the S3 bucket containing the trained model"
  type        = string
}

variable "source_stream_arn" {
  description = "ARN of the source Kinesis stream (used by CloudWatch)"
  type        = string
}
