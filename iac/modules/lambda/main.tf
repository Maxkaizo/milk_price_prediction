resource "aws_lambda_function" "tfid_lambda" {
  function_name = var.lambda_name
  role          = var.lambda_exec_role_arn
  package_type  = "Image"
  image_uri     = var.image_uri
  timeout       = var.lambda_timeout
  memory_size   = var.lambda_memory
}
