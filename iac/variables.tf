# 🌐 Región de AWS
variable "aws_region" {
  description = "AWS region for deploying all resources"
  type        = string
  default     = "us-east-1"
}

# 🏷️ Identificador del proyecto (usado como prefijo en todos los recursos)
variable "project_id" {
  description = "Unique identifier for the project (used as tfid_<project_id>)"
  type        = string
}

# 🐳 Nombre base del repositorio ECR
variable "repository_name" {
  description = "Base name for the ECR repository (project_id will be prepended)"
  type        = string
}

# 🧠 Nombre base de la función Lambda
variable "lambda_name" {
  description = "Base name for the Lambda function (project_id will be prepended)"
  type        = string
}

# 📦 Nombre base de la API Gateway
variable "api_name" {
  description = "Base name for the API Gateway (project_id will be prepended)"
  type        = string
}

# 📁 Recursos S3 a los que Lambda debe tener acceso
variable "s3_resources" {
  description = "List of S3 ARNs that the Lambda function needs read access to"
  type        = list(string)
}

# ⏱ Tiempo máximo de ejecución de Lambda
variable "lambda_timeout" {
  description = "Timeout for the Lambda function (in seconds)"
  type        = number
  default     = 60
}

# 💾 Memoria para la Lambda
variable "lambda_memory" {
  description = "Memory size for the Lambda function (in MB)"
  type        = number
  default     = 3008
}

# 🌐 Clave de la ruta en API Gateway (ej: POST /predict)
variable "route_key" {
  description = "HTTP route key for API Gateway (e.g. POST /predict)"
  type        = string
  default     = "POST /predict"
}

# 🧾 Nombre del stage de la API
variable "stage_name" {
  description = "Name of the API Gateway stage"
  type        = string
  default     = "default"
}
