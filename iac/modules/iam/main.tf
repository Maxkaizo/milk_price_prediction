resource "aws_iam_role" "tfid_lambda_exec_role" {
  name = "${var.name_prefix}_lambda_exec_role"

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

resource "aws_iam_role_policy_attachment" "tfid_basic_execution" {
  role       = aws_iam_role.tfid_lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_policy" "tfid_s3_read_policy" {
  name        = "${var.name_prefix}_s3_read_policy"
  description = "Allows Lambda to read from S3 resources"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = [
          "s3:*",
          "s3-object-lambda:*"
        ],
#        Resource = var.s3_resources
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "tfid_s3_read_attachment" {
  role       = aws_iam_role.tfid_lambda_exec_role.name
  policy_arn = aws_iam_policy.tfid_s3_read_policy.arn
}
