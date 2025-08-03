variable "name_prefix" {
  description = "Prefix used to name IAM resources (usually tfid + project_id)"
  type        = string
}

variable "s3_resources" {
  description = "List of S3 ARNs that Lambda is allowed to read from"
  type        = list(string)
}
