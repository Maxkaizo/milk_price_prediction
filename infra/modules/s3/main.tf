#############################################
# modules/s3/main.tf
#############################################

resource "aws_s3_bucket" "s3_bucket" {
  bucket        = var.bucket_name
  force_destroy = true
}

output "name" {
  value = aws_s3_bucket.s3_bucket.bucket
}
