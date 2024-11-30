resource "aws_lambda_function" "stack_for_dev" {
  function_name = local.project_name
  role          = aws_iam_role.stack_for_dev.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.stack_for_dev.repository_url}:latest"
  tags          = local.common_tags
  timeout       = 30

  lifecycle {
    ignore_changes = [
      environment
    ]
  }
}

# Add Lambda permission for API Gateway
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.stack_for_dev.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.stack_for_dev.execution_arn}/*/*"
}
