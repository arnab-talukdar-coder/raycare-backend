data "archive_file" "package" {
  type        = "zip"
  source_dir  = var.source_dir
  output_path = var.output_path
}

resource "aws_lambda_function" "this" {
  function_name    = var.function_name
  filename         = data.archive_file.package.output_path
  source_code_hash = data.archive_file.package.output_base64sha256
  handler          = var.handler
  role             = var.role_arn
  runtime          = var.runtime
  timeout          = var.timeout
  memory_size      = var.memory_size
  layers           = var.layers

  environment {
    variables = var.environment
  }

  tracing_config {
    mode = "Active"
  }
}
