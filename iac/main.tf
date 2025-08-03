provider "aws" {
  region = var.aws_region
}

# 🔐 IAM Module
module "iam" {
  source       = "./modules/iam"
  name_prefix  = "tfid_${var.project_id}"
  s3_resources = var.s3_resources
}

# 🐳 ECR Module
module "ecr" {
  source          = "./modules/ecr"
  name_prefix     = "tfid_${var.project_id}"
  repository_name = var.repository_name
}

# 🔁 Push Docker image to ECR (local exec)
resource "null_resource" "tfid_push_lambda_image" {
  provisioner "local-exec" {
    command = <<EOT
      aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${module.ecr.repository_url}
      docker build --platform linux/amd64 -t ${module.ecr.repository_url}:latest -f ./code/Dockerfile ./code --no-cache
      docker push --platform linux/amd64 ${module.ecr.repository_url}:latest
    EOT
  }

  triggers = {
    dockerfile_hash = md5(file("./code/Dockerfile"))
    handler_hash    = md5(file("./code/handler.py"))
  }
}

# 📦 Esperar a que la imagen esté disponible
data "aws_ecr_image" "tfid_lambda_image" {
  depends_on      = [null_resource.tfid_push_lambda_image]
  repository_name = module.ecr.repository_name
  image_tag       = "latest"
}


# 🧠 Lambda Module
module "lambda" {
  source               = "./modules/lambda"
  lambda_name          = "tfid_${var.project_id}_${var.lambda_name}"
  lambda_exec_role_arn = module.iam.lambda_exec_role_arn
  image_uri            = "${module.ecr.repository_url}:${data.aws_ecr_image.tfid_lambda_image.image_tag}"
  lambda_timeout       = var.lambda_timeout
  lambda_memory        = var.lambda_memory
}

# 🌐 API Gateway Module
module "api_gw" {
  source               = "./modules/api_gw"
  api_name             = "tfid_${var.project_id}_${var.api_name}"
  lambda_invoke_arn    = module.lambda.lambda_invoke_arn
  lambda_function_name = module.lambda.lambda_function_name
  route_key            = var.route_key
  stage_name           = var.stage_name
}
