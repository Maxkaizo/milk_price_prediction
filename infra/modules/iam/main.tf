#############################################
# modules/iam/main.tf
#############################################

resource "aws_iam_role" "iam_lambda" {
  name = "iam_${var.lambda_function_name}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = ["lambda.amazonaws.com", "kinesis.amazonaws.com"]
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_policy" "allow_kinesis_processing" {
  name        = "allow_kinesis_processing_${var.lambda_function_name}"
  description = "IAM policy for processing Kinesis stream"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = ["kinesis:ListShards", "kinesis:ListStreams", "kinesis:*"],
        Resource = "arn:aws:kinesis:*:*:*",
        Effect   = "Allow"
      },
      {
        Action = ["stream:GetRecord", "stream:GetShardIterator", "stream:DescribeStream", "stream:*"],
        Resource = "arn:aws:stream:*:*:*",
        Effect   = "Allow"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "kinesis_processing" {
  role       = aws_iam_role.iam_lambda.name
  policy_arn = aws_iam_policy.allow_kinesis_processing.arn
}

resource "aws_iam_role_policy" "inline_lambda_policy" {
  name   = "LambdaInlinePolicy"
  role   = aws_iam_role.iam_lambda.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = ["kinesis:PutRecords", "kinesis:PutRecord"],
        Resource = var.output_stream_arn
      }
    ]
  })
}

resource "aws_iam_policy" "allow_logging" {
  name        = "allow_logging_${var.lambda_function_name}"
  description = "IAM policy for CloudWatch logging"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
        Resource = "arn:aws:logs:*:*:*",
        Effect   = "Allow"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.iam_lambda.name
  policy_arn = aws_iam_policy.allow_logging.arn
}

resource "aws_iam_policy" "lambda_s3_role_policy" {
  name        = "lambda_s3_policy_${var.lambda_function_name}"
  description = "IAM policy for accessing S3 and CloudWatch"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = ["s3:ListAllMyBuckets", "s3:GetBucketLocation", "s3:*"],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = "s3:*",
        Resource = [
          "arn:aws:s3:::${var.model_bucket}",
          "arn:aws:s3:::${var.model_bucket}/*"
        ]
      },
      {
        Effect = "Allow",
        Action = ["autoscaling:Describe*", "cloudwatch:*", "logs:*", "sns:*"],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_s3_access" {
  role       = aws_iam_role.iam_lambda.name
  policy_arn = aws_iam_policy.lambda_s3_role_policy.arn
}
