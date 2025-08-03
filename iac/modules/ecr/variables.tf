variable "name_prefix" {
  description = "Prefix used to name ECR resources (e.g., tfid_projectid)"
  type        = string
}

variable "repository_name" {
  description = "Base name of the ECR repository (e.g., milk-api-lambda)"
  type        = string
}
