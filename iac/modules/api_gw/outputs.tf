output "api_url" {
  description = "Public URL of the API Gateway endpoint"
  value       = "${aws_apigatewayv2_api.tfid_api.api_endpoint}/${aws_apigatewayv2_stage.tfid_stage.name}"
}
