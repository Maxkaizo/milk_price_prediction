variable "ecr_repo_name" {
  description = "Name of the ECR repository"
  type        = string
}

variable "lambda_function_local_path" {
  description = "Path to the Python handler file"
  type        = string
}

variable "docker_image_local_path" {
  description = "Path to the Dockerfile"
  type        = string
}

variable "ecr_image_tag" {
  description = "Tag to assign to the Docker image"
  type        = string
  default     = "latest"
}

variable "region" {
  description = "AWS region"
  type        = string
}

variable "account_id" {
  description = "AWS account ID"
  type        = string
}
