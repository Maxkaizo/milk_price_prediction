#############################################
# modules/lambda/main.tf
#############################################

resource "aws_lambda_function" "kinesis_lambda" {
  function_name = var.lambda_function_name
  image_uri     = var.image_uri
  package_type  = "Image"
  role          = var.lambda_role_arn

  tracing_config {
    mode = "Active"
  }

  environment {
    variables = {
      PREDICTIONS_STREAM_NAME = var.output_stream_name
      MODEL_BUCKET            = var.model_bucket
    }
  }

  timeout = 180
}

resource "aws_lambda_function_event_invoke_config" "kinesis_lambda_event" {
  function_name                 = aws_lambda_function.kinesis_lambda.function_name
  maximum_event_age_in_seconds = 60
  maximum_retry_attempts       = 0
}

resource "aws_lambda_event_source_mapping" "kinesis_mapping" {
  event_source_arn  = var.source_stream_arn
  function_name     = aws_lambda_function.kinesis_lambda.arn
  starting_position = "LATEST"

  depends_on = [
    var.kinesis_mapping_dependency
  ]
}

output "lambda_function_name" {
  value = aws_lambda_function.kinesis_lambda.function_name
}

