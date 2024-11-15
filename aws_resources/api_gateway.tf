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
      rest_api    = aws_api_gateway_rest_api.stack_for_dev.body
      method      = aws_api_gateway_method.generate_dockerfile.id
      integration = aws_api_gateway_integration.generate_dockerfile.id
      resource    = aws_api_gateway_resource.generate_dockerfile.id
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
      burst_limit = 1
      rate_limit  = 1
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
}

resource "aws_api_gateway_method" "generate_dockerfile" {
  authorization = "NONE"
  http_method   = "GET"
  resource_id   = aws_api_gateway_rest_api.stack_for_dev.root_resource_id
  rest_api_id   = aws_api_gateway_rest_api.stack_for_dev.id
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

resource "aws_api_gateway_resource" "generate_dockerfile" {
  path_part   = "generate-dockerfile"
  parent_id   = aws_api_gateway_rest_api.stack_for_dev.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.stack_for_dev.id
}

output "api_gateway_invoke_url" {
  value = aws_api_gateway_stage.prod.invoke_url
}
