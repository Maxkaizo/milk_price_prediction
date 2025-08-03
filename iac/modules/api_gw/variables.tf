variable "api_name" {
  description = "Full name of the API Gateway (should include tfid_project_id)"
  type        = string
}

variable "lambda_invoke_arn" {
  description = "Invoke ARN of the Lambda function to integrate"
  type        = string
}

variable "lambda_function_name" {
  description = "Name of the Lambda function (used in permission block)"
  type        = string
}

variable "route_key" {
  description = "Route key for the API Gateway (e.g., POST /predict)"
  type        = string
  default     = "POST /predict"
}

variable "stage_name" {
  description = "Name of the stage (e.g., default, v1, prod)"
  type        = string
  default     = "default"
}
