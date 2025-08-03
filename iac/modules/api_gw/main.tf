resource "aws_apigatewayv2_api" "tfid_api" {
  name          = var.api_name
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "tfid_integration" {
  api_id                 = aws_apigatewayv2_api.tfid_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = var.lambda_invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "tfid_route" {
  api_id    = aws_apigatewayv2_api.tfid_api.id
  route_key = var.route_key
  target    = "integrations/${aws_apigatewayv2_integration.tfid_integration.id}"
}

resource "aws_apigatewayv2_stage" "tfid_stage" {
  api_id      = aws_apigatewayv2_api.tfid_api.id
  name        = var.stage_name
  auto_deploy = true
}

resource "aws_lambda_permission" "tfid_apigw_permission" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.tfid_api.execution_arn}/*/*"
}
