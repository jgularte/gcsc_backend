provider "aws" {
  profile = "personal"
  region = var.aws_region
}

resource "aws_lambda_function" "lambda" {
  function_name = var.function_name
  filename = var.lambda_src_location
  handler = var.handler
  role = var.role_arn
  runtime = "python3.8"
  timeout = var.timeout
  memory_size = var.memory
  source_code_hash = filebase64sha256(var.lambda_src_location)

  environment {
    variables = {
      environment = var.environment
    }
  }

  tracing_config {
    mode = var.tracing_mode
  }

  tags = {
    project_name = "GularteCabinSharedCalendar"
    environment = var.environment
  }
}