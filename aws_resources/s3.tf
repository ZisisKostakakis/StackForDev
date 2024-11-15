resource "aws_s3_bucket" "dockerfiles" {
  bucket = "stackfordev-dockerfiles"
}

resource "aws_s3_bucket_public_access_block" "dockerfiles" {
  bucket = aws_s3_bucket.dockerfiles.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}