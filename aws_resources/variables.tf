variable "AWS_ACCESS_KEY_ID" {
  type        = string
  description = "AWS access key ID"
  sensitive   = true
}

variable "AWS_SECRET_ACCESS_KEY" {
  type        = string
  description = "AWS secret access key"
  sensitive   = true
}

variable "AWS_ACCOUNT_ID" {
  type        = string
  description = "AWS account ID"
}

variable "AWS_REGION" {
  type        = string
  description = "AWS region for resources"
}

variable "api_key_required" {
  description = "Whether API key is required for methods"
  type        = bool
  default     = true
}

variable "aws_api_gateway_integration" {
  type        = string
  default     = "AWS_PROXY"
  description = "Type of API Gateway integration"
}
