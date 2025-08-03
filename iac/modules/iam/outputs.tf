output "lambda_exec_role_arn" {
  description = "ARN of the IAM role for Lambda execution"
  value       = aws_iam_role.tfid_lambda_exec_role.arn
}
