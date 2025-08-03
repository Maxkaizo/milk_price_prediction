output "repository_url" {
  description = "URL of the ECR repository (used as image_uri for Lambda)"
  value       = aws_ecr_repository.tfid_repo.repository_url
}

output "repository_name" {
  description = "Name of the ECR repository"
  value       = aws_ecr_repository.tfid_repo.name
}
