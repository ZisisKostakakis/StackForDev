resource "aws_api_gateway_rest_api" "stack_for_dev" {
  name        = "stack-for-dev"
  description = "API for StackForDev"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_deployment" "stack_for_dev" {
  rest_api_id = aws_api_gateway_rest_api.stack_for_dev.id

  triggers = {
    redeployment = sha1(jsonencode({
      rest_api           = aws_api_gateway_rest_api.stack_for_dev.body
      method             = aws_api_gateway_method.generate_dockerfile.id
      integration        = aws_api_gateway_integration.generate_dockerfile.id
      resource           = aws_api_gateway_resource.generate_dockerfile.id
      options_method     = aws_api_gateway_method.options.id
      options_integration = aws_api_gateway_integration.options.id
    }))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "prod" {
  deployment_id = aws_api_gateway_deployment.stack_for_dev.id
  rest_api_id   = aws_api_gateway_rest_api.stack_for_dev.id
  stage_name    = "prod"
}

resource "aws_api_gateway_api_key" "stack_for_dev" {
  name        = "stack-for-dev"
  enabled     = true
  description = "API key for StackForDev"
}

resource "aws_api_gateway_usage_plan" "stack_for_dev" {
  name         = "stack-for-dev"
  description  = "Usage plan for StackForDev"
  product_code = "stack-for-dev"

  api_stages {
    api_id = aws_api_gateway_rest_api.stack_for_dev.id
    stage  = "prod"

    throttle {
      burst_limit = 20
      rate_limit  = 10
      path        = "*/*"
    }
  }

  quota_settings {
    limit  = 10000
    offset = 0
    period = "MONTH"
  }

  throttle_settings {
    burst_limit = 1
    rate_limit  = 1
  }
  depends_on = [
    aws_api_gateway_stage.prod
  ]
}

resource "aws_api_gateway_usage_plan_key" "stack_for_dev" {
  key_id        = aws_api_gateway_api_key.stack_for_dev.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.stack_for_dev.id
}

resource "aws_api_gateway_method_settings" "stack_for_dev" {
  rest_api_id = aws_api_gateway_rest_api.stack_for_dev.id
  stage_name  = "prod"
  method_path = "*/*"

  settings {
    throttling_burst_limit = 1
    throttling_rate_limit  = 1
  }
  depends_on = [
    aws_api_gateway_stage.prod,
    aws_api_gateway_method.generate_dockerfile
  ]
}

resource "aws_api_gateway_resource" "generate_dockerfile" {
  path_part   = "generate-dockerfile"
  parent_id   = aws_api_gateway_rest_api.stack_for_dev.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.stack_for_dev.id
}

resource "aws_api_gateway_method" "generate_dockerfile" {
  authorization    = "NONE"
  http_method      = "POST"
  resource_id      = aws_api_gateway_resource.generate_dockerfile.id
  rest_api_id      = aws_api_gateway_rest_api.stack_for_dev.id
  api_key_required = "true"
}

resource "aws_api_gateway_integration" "generate_dockerfile" {
  timeout_milliseconds    = 20000
  http_method             = aws_api_gateway_method.generate_dockerfile.http_method
  resource_id             = aws_api_gateway_method.generate_dockerfile.resource_id
  rest_api_id             = aws_api_gateway_method.generate_dockerfile.rest_api_id
  type                    = var.aws_api_gateway_integration
  integration_http_method = "POST"
  uri                     = aws_lambda_function.stack_for_dev.invoke_arn
}

resource "aws_api_gateway_method_response" "response_200" {
  rest_api_id = aws_api_gateway_rest_api.stack_for_dev.id
  resource_id = aws_api_gateway_resource.generate_dockerfile.id
  http_method = aws_api_gateway_method.generate_dockerfile.http_method
  status_code = "200"
  response_models = {
    "application/json" = "Empty"
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"  = true
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
  }
  depends_on = [
    aws_api_gateway_method.generate_dockerfile
  ]
}

# CORS OPTIONS method
resource "aws_api_gateway_method" "options" {
  rest_api_id   = aws_api_gateway_rest_api.stack_for_dev.id
  resource_id   = aws_api_gateway_resource.generate_dockerfile.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "options" {
  rest_api_id = aws_api_gateway_rest_api.stack_for_dev.id
  resource_id = aws_api_gateway_resource.generate_dockerfile.id
  http_method = aws_api_gateway_method.options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "options_200" {
  rest_api_id = aws_api_gateway_rest_api.stack_for_dev.id
  resource_id = aws_api_gateway_resource.generate_dockerfile.id
  http_method = aws_api_gateway_method.options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }

  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_integration_response" "options" {
  rest_api_id = aws_api_gateway_rest_api.stack_for_dev.id
  resource_id = aws_api_gateway_resource.generate_dockerfile.id
  http_method = aws_api_gateway_method.options.http_method
  status_code = aws_api_gateway_method_response.options_200.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

output "api_gateway_invoke_url" {
  value = aws_api_gateway_stage.prod.invoke_url
}
