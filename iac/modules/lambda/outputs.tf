output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.tfid_lambda.function_name
}

output "lambda_invoke_arn" {
  description = "Invoke ARN of the Lambda function (used by API Gateway)"
  value       = aws_lambda_function.tfid_lambda.invoke_arn
}
