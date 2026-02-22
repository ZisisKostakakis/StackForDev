# CloudWatch Log Group with 30-day retention
resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${aws_lambda_function.stack_for_dev.function_name}"
  retention_in_days = 30
  tags              = local.common_tags
}

# SNS Topic for alarm notifications
resource "aws_sns_topic" "lambda_alerts" {
  name = "${local.project_name}-alerts"
  tags = local.common_tags
}

# CloudWatch Alarm: Lambda error rate
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "${local.project_name}-errors"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Lambda function error count >= 5 in 5 minutes"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.stack_for_dev.function_name
  }

  alarm_actions = [aws_sns_topic.lambda_alerts.arn]
  ok_actions    = [aws_sns_topic.lambda_alerts.arn]

  tags = local.common_tags
}

# CloudWatch Alarm: Lambda throttle rate
resource "aws_cloudwatch_metric_alarm" "lambda_throttles" {
  alarm_name          = "${local.project_name}-throttles"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "Throttles"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "Lambda throttle count >= 10 in 5 minutes"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.stack_for_dev.function_name
  }

  alarm_actions = [aws_sns_topic.lambda_alerts.arn]

  tags = local.common_tags
}
