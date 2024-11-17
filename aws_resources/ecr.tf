resource "aws_ecr_repository" "stack_for_dev" {
  name                 = "stack-for-dev"
  image_tag_mutability = "MUTABLE"
  force_delete         = false
}

resource "aws_ecr_repository_policy" "stack_for_dev" {
  repository = aws_ecr_repository.stack_for_dev.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid    = "AllowPushPull"
      Effect = "Allow"
      Principal = {
        AWS = "arn:aws:iam::${var.AWS_ACCOUNT_ID}:root"
      }
      Action = sort([
        "ecr:BatchCheckLayerAvailability",
        "ecr:BatchGetImage",
        "ecr:CompleteLayerUpload",
        "ecr:GetDownloadUrlForLayer",
        "ecr:InitiateLayerUpload",
        "ecr:PutImage",
        "ecr:UploadLayerPart"
      ])
    }]
  })
}

resource "aws_ecr_lifecycle_policy" "stack_for_dev" {
  repository = aws_ecr_repository.stack_for_dev.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 3 images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 3
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
} 
