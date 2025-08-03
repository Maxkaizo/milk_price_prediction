variable "lambda_name" {
  description = "Full name of the Lambda function (prefixed with tfid_project_id)"
  type        = string
}

variable "lambda_exec_role_arn" {
  description = "ARN of the IAM role for Lambda to assume"
  type        = string
}

variable "image_uri" {
  description = "URI of the container image stored in ECR"
  type        = string
}

variable "lambda_timeout" {
  description = "Lambda timeout in seconds"
  type        = number
  default     = 60
}

variable "lambda_memory" {
  description = "Memory allocated to Lambda (in MB)"
  type        = number
  default     = 3008
}
