resource "aws_ecr_repository" "tfid_repo" {
  name                 = "${var.name_prefix}_${var.repository_name}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }

  force_delete = true
}