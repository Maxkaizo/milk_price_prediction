# ✅ AWS Provider Configuration
# Specifies the AWS region where all resources will be deployed.
provider "aws" {
  region = "us-east-1"
}

# 🐳 Amazon ECR Repository for Lambda Container Image
# This creates a repository that will store the container image for Lambda.
resource "aws_ecr_repository" "milk_api_lambda_repo" {
  name                 = "milk-api-lambda"
  image_tag_mutability = "MUTABLE"  # Allows overwriting tags like "latest"

  image_scanning_configuration {
    scan_on_push = false  # Disable automatic image scanning when pushing
  }

  force_delete = true  # Allows deletion even if images are still in the repo
}

# 🔁 Resource to build and push the Docker image to ECR
# Terraform is not designed to build Docker images, but we use a null_resource with local-exec
# to run local shell commands that handle image creation and upload.
resource "null_resource" "push_lambda_image" {
  provisioner "local-exec" {
    command = <<EOT
      # Authenticate with ECR
      aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 438480637738.dkr.ecr.us-east-1.amazonaws.com

      # Build Docker image from Dockerfile.lambda (assumes you're one level deep)
      docker build --platform linux/amd64 -t 438480637738.dkr.ecr.us-east-1.amazonaws.com/milk-api-lambda:latest -f ../Dockerfile.lambda ../ --no-cache

      # Push the image to ECR
      docker push --platform linux/amd64 438480637738.dkr.ecr.us-east-1.amazonaws.com/milk-api-lambda:latest
    EOT
  }

  # This ensures the image is rebuilt and pushed when these files change
  triggers = {
    dockerfile_hash = md5(file("../Dockerfile.lambda"))
    handler_hash    = md5(file("../handler.py"))
  }
}

# ⏳ Wait until image is available before continuing
# This ensures downstream resources can safely use the image.
data "aws_ecr_image" "lambda_image" {
  depends_on      = [null_resource.push_lambda_image]
  repository_name = aws_ecr_repository.milk_api_lambda_repo.name
  image_tag       = "latest"
}

# 🔐 IAM Role for Lambda execution
# This role allows Lambda to run and write logs to CloudWatch.
resource "aws_iam_role" "lambda_exec_role" {
  name = "milk-api-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

# 📎 Attach basic execution policy to the IAM role
# Enables the Lambda function to write logs to CloudWatch.
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# 📜 IAM Policy to allow Lambda to read from the S3 model bucket
resource "aws_iam_policy" "allow_s3_read" {
  name        = "AllowS3ReadFromModelBucket"
  description = "Allows Lambda to perform GetObject on the ML model bucket"

  # El documento de la política en formato JSON
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = [
          "s3:*",
          "s3-object-lambda:*"
        ],
        Resource = [
          "*" # <-- Nombre del bucket hardcodeado
        ]
      }
    ]
  })
}

# 📎 Attach the new S3 policy to the Lambda's execution role
resource "aws_iam_role_policy_attachment" "lambda_s3_read_attachment" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.allow_s3_read.arn
}


# 🧠 Create Lambda Function from Container Image
# This function is created using the container image stored in ECR.
resource "aws_lambda_function" "milk_api_lambda" {
  function_name = "milk-api-lambda"
  role          = aws_iam_role.lambda_exec_role.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.milk_api_lambda_repo.repository_url}:${data.aws_ecr_image.lambda_image.image_tag}"
  timeout       = 70  # <--- Aumentar este valor (ej. a 30 o 60 segundos)
  memory_size   = 3008 # <--- Opcional: Aumentar la memoria también acelera el cold start
}

# 🌐 Create API Gateway (HTTP API, v2)
# Exposes the Lambda function via a public REST endpoint.
resource "aws_apigatewayv2_api" "milk_api_gateway" {
  name          = "milk-api"
  protocol_type = "HTTP"
}

# 🔗 Connect API Gateway to Lambda
# Defines how API Gateway forwards requests to the Lambda function.
resource "aws_apigatewayv2_integration" "milk_api_integration" {
  api_id                  = aws_apigatewayv2_api.milk_api_gateway.id
  integration_type        = "AWS_PROXY"  # Direct proxy integration
  integration_uri         = aws_lambda_function.milk_api_lambda.invoke_arn
  integration_method      = "POST"
  payload_format_version  = "2.0"
}

# 🚪 Create a stage to expose the API
# This defines the public URL path where the API will be accessible.
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.milk_api_gateway.id
  name        = "default"
  auto_deploy = true
}

resource "aws_apigatewayv2_route" "predict_route" {
  api_id    = aws_apigatewayv2_api.milk_api_gateway.id
  route_key = "POST /predict"  # Defines the method and path
  target    = "integrations/${aws_apigatewayv2_integration.milk_api_integration.id}"
}

# 🔄 Permission: allow API Gateway to invoke Lambda
resource "aws_lambda_permission" "api_gateway_invoke" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.milk_api_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.milk_api_gateway.execution_arn}/*/*"
}


# ✅ Output: the public URL of the API
output "api_url" {
  value = "${aws_apigatewayv2_api.milk_api_gateway.api_endpoint}/default"
}
