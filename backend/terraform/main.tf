data "aws_caller_identity" "current" {}

locals {
  table_names = {
    users                = "${var.project_name}-users"
    sessions             = "${var.project_name}-sessions"
    services             = "${var.project_name}-services"
    service_requests     = "${var.project_name}-service-requests"
    assignments          = "${var.project_name}-assignments"
    health_events        = "${var.project_name}-health-events"
    emergency_cases      = "${var.project_name}-emergency-cases"
    notifications        = "${var.project_name}-notifications"
    subscriptions        = "${var.project_name}-subscriptions"
    medication_reminders = "${var.project_name}-medication-reminders"
  }

  lambda_environment = {
    AWS_REGION                 = var.aws_region
    JWT_SECRET                 = var.jwt_secret
    JWT_ISSUER                 = "${var.project_name}-api"
    USERS_TABLE                = local.table_names.users
    SESSIONS_TABLE             = local.table_names.sessions
    SERVICES_TABLE             = local.table_names.services
    SERVICE_REQUESTS_TABLE     = local.table_names.service_requests
    ASSIGNMENTS_TABLE          = local.table_names.assignments
    HEALTH_EVENTS_TABLE        = local.table_names.health_events
    EMERGENCY_CASES_TABLE      = local.table_names.emergency_cases
    NOTIFICATIONS_TABLE        = local.table_names.notifications
    SUBSCRIPTIONS_TABLE        = local.table_names.subscriptions
    MEDICATION_REMINDERS_TABLE = local.table_names.medication_reminders
    MEDICAL_RECORDS_BUCKET     = aws_s3_bucket.medical_records.id
    SMS_ENABLED                = "false"
    OTP_DEBUG_MODE             = "true"
  }
  lambda_layers = var.dependency_layer_arn != "" ? [var.dependency_layer_arn] : []

  route_to_lambda = {
    "POST /auth/send-otp"                = "auth"
    "POST /auth/verify-otp"              = "auth"
    "POST /auth/register"                = "auth"
    "POST /auth/logout"                  = "auth"
    "GET /patient/profile"               = "patient"
    "POST /patient/edit-profile"         = "patient"
    "POST /health/raise-service"         = "patient"
    "POST /patient/book-appointment"     = "patient"
    "GET /patient/appointments"          = "patient"
    "GET /patient/history"               = "patient"
    "POST /health/sos"                   = "patient"
    "GET /nurse/assigned-services"       = "nurse"
    "POST /nurse/start-visit"            = "nurse"
    "POST /nurse/submit-visit"           = "nurse"
    "GET /doctor/appointments"           = "doctor"
    "POST /doctor/generate-prescription" = "doctor"
    "POST /doctor/add-medication"        = "doctor"
    "GET /doctor/patient-history"        = "doctor"
    "GET /admin/service-requests"        = "admin"
    "POST /admin/assign-nurse"           = "admin"
    "POST /superadmin/create-user"       = "super_admin"
    "POST /superadmin/assign-doctor"     = "super_admin"
    "POST /superadmin/create-service"    = "super_admin"
    "GET /superadmin/all-users"          = "super_admin"
    "GET /superadmin/system-data"        = "super_admin"
    "POST /subscription/purchase"        = "subscription"
    "GET /subscription/status"           = "subscription"
  }
}

resource "aws_dynamodb_table" "users" {
  name         = local.table_names.users
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "phone_number"
  range_key    = "user_name"

  attribute {
    name = "phone_number"
    type = "S"
  }

  attribute {
    name = "user_name"
    type = "S"
  }
}

resource "aws_dynamodb_table" "sessions" {
  name         = local.table_names.sessions
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "session_id"

  attribute {
    name = "session_id"
    type = "S"
  }

  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }
}

resource "aws_dynamodb_table" "services" {
  name         = local.table_names.services
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "UUID"

  attribute {
    name = "UUID"
    type = "S"
  }
}

resource "aws_dynamodb_table" "service_requests" {
  name         = local.table_names.service_requests
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "UUID"

  attribute {
    name = "UUID"
    type = "S"
  }
}

resource "aws_dynamodb_table" "assignments" {
  name         = local.table_names.assignments
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "UUID"

  attribute {
    name = "UUID"
    type = "S"
  }
}

resource "aws_dynamodb_table" "health_events" {
  name         = local.table_names.health_events
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "UUID"

  attribute {
    name = "UUID"
    type = "S"
  }
}

resource "aws_dynamodb_table" "emergency_cases" {
  name         = local.table_names.emergency_cases
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "UUID"

  attribute {
    name = "UUID"
    type = "S"
  }
}

resource "aws_dynamodb_table" "notifications" {
  name         = local.table_names.notifications
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "UUID"

  attribute {
    name = "UUID"
    type = "S"
  }
}

resource "aws_dynamodb_table" "subscriptions" {
  name         = local.table_names.subscriptions
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "UUID"

  attribute {
    name = "UUID"
    type = "S"
  }
}

resource "aws_dynamodb_table" "medication_reminders" {
  name         = local.table_names.medication_reminders
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "UUID"

  attribute {
    name = "UUID"
    type = "S"
  }
}

resource "aws_s3_bucket" "medical_records" {
  bucket = var.medical_records_bucket
}

resource "aws_s3_bucket_public_access_block" "medical_records" {
  bucket = aws_s3_bucket.medical_records.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "medical_records" {
  bucket = aws_s3_bucket.medical_records.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "medical_records" {
  bucket = aws_s3_bucket.medical_records.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-alerts"
}

resource "aws_iam_role" "lambda_exec" {
  name = "${var.project_name}-${var.stage}-lambda-exec"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_xray" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess"
}

resource "aws_iam_role_policy" "lambda_data_access" {
  name = "${var.project_name}-${var.stage}-lambda-data-access"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.users.arn,
          aws_dynamodb_table.sessions.arn,
          aws_dynamodb_table.services.arn,
          aws_dynamodb_table.service_requests.arn,
          aws_dynamodb_table.assignments.arn,
          aws_dynamodb_table.health_events.arn,
          aws_dynamodb_table.emergency_cases.arn,
          aws_dynamodb_table.notifications.arn,
          aws_dynamodb_table.subscriptions.arn,
          aws_dynamodb_table.medication_reminders.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.medical_records.arn,
          "${aws_s3_bucket.medical_records.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = ["*"]
      }
    ]
  })
}

module "auth_lambda" {
  source        = "./modules/lambda"
  function_name = "${var.project_name}-${var.stage}-auth"
  source_dir    = "${path.module}/.."
  output_path   = "${path.module}/auth.zip"
  handler       = "src.handlers.auth.lambda_handler"
  role_arn      = aws_iam_role.lambda_exec.arn
  environment   = local.lambda_environment
  layers        = local.lambda_layers
}

module "patient_lambda" {
  source        = "./modules/lambda"
  function_name = "${var.project_name}-${var.stage}-patient"
  source_dir    = "${path.module}/.."
  output_path   = "${path.module}/patient.zip"
  handler       = "src.handlers.patient.lambda_handler"
  role_arn      = aws_iam_role.lambda_exec.arn
  environment   = local.lambda_environment
  layers        = local.lambda_layers
}

module "nurse_lambda" {
  source        = "./modules/lambda"
  function_name = "${var.project_name}-${var.stage}-nurse"
  source_dir    = "${path.module}/.."
  output_path   = "${path.module}/nurse.zip"
  handler       = "src.handlers.nurse.lambda_handler"
  role_arn      = aws_iam_role.lambda_exec.arn
  environment   = local.lambda_environment
  layers        = local.lambda_layers
}

module "doctor_lambda" {
  source        = "./modules/lambda"
  function_name = "${var.project_name}-${var.stage}-doctor"
  source_dir    = "${path.module}/.."
  output_path   = "${path.module}/doctor.zip"
  handler       = "src.handlers.doctor.lambda_handler"
  role_arn      = aws_iam_role.lambda_exec.arn
  environment   = local.lambda_environment
  layers        = local.lambda_layers
}

module "admin_lambda" {
  source        = "./modules/lambda"
  function_name = "${var.project_name}-${var.stage}-admin"
  source_dir    = "${path.module}/.."
  output_path   = "${path.module}/admin.zip"
  handler       = "src.handlers.admin.lambda_handler"
  role_arn      = aws_iam_role.lambda_exec.arn
  environment   = local.lambda_environment
  layers        = local.lambda_layers
}

module "super_admin_lambda" {
  source        = "./modules/lambda"
  function_name = "${var.project_name}-${var.stage}-super-admin"
  source_dir    = "${path.module}/.."
  output_path   = "${path.module}/super-admin.zip"
  handler       = "src.handlers.super_admin.lambda_handler"
  role_arn      = aws_iam_role.lambda_exec.arn
  environment   = local.lambda_environment
  layers        = local.lambda_layers
}

module "subscription_lambda" {
  source        = "./modules/lambda"
  function_name = "${var.project_name}-${var.stage}-subscription"
  source_dir    = "${path.module}/.."
  output_path   = "${path.module}/subscription.zip"
  handler       = "src.handlers.subscription.lambda_handler"
  role_arn      = aws_iam_role.lambda_exec.arn
  environment   = local.lambda_environment
  layers        = local.lambda_layers
}

module "scheduler_lambda" {
  source        = "./modules/lambda"
  function_name = "${var.project_name}-${var.stage}-medication-scheduler"
  source_dir    = "${path.module}/.."
  output_path   = "${path.module}/medication-scheduler.zip"
  handler       = "src.scheduler.medication_scheduler.lambda_handler"
  role_arn      = aws_iam_role.lambda_exec.arn
  environment   = local.lambda_environment
  layers        = local.lambda_layers
}

locals {
  api_lambdas = {
    auth         = module.auth_lambda.invoke_arn
    patient      = module.patient_lambda.invoke_arn
    nurse        = module.nurse_lambda.invoke_arn
    doctor       = module.doctor_lambda.invoke_arn
    admin        = module.admin_lambda.invoke_arn
    super_admin  = module.super_admin_lambda.invoke_arn
    subscription = module.subscription_lambda.invoke_arn
  }

  api_lambda_names = {
    auth         = module.auth_lambda.function_name
    patient      = module.patient_lambda.function_name
    nurse        = module.nurse_lambda.function_name
    doctor       = module.doctor_lambda.function_name
    admin        = module.admin_lambda.function_name
    super_admin  = module.super_admin_lambda.function_name
    subscription = module.subscription_lambda.function_name
  }
}

module "http_api" {
  source          = "./modules/http_api"
  name            = "${var.project_name}-${var.stage}-http-api"
  stage_name      = "$default"
  lambdas         = local.api_lambdas
  route_to_lambda = local.route_to_lambda
}

resource "aws_lambda_permission" "allow_api_gateway" {
  for_each = local.api_lambda_names

  statement_id  = "AllowExecutionFromAPIGateway-${each.key}"
  action        = "lambda:InvokeFunction"
  function_name = each.value
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.aws_region}:${data.aws_caller_identity.current.account_id}:${module.http_api.api_id}/*/*"
}

resource "aws_iam_role" "scheduler_invoke" {
  name = "${var.project_name}-${var.stage}-scheduler-invoke"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = "sts:AssumeRole"
      Principal = {
        Service = "scheduler.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "scheduler_invoke_lambda" {
  name = "${var.project_name}-${var.stage}-scheduler-invoke-lambda"
  role = aws_iam_role.scheduler_invoke.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "lambda:InvokeFunction"
      Resource = module.scheduler_lambda.arn
    }]
  })
}

resource "aws_scheduler_schedule" "medication_reminder" {
  name                = "${var.project_name}-${var.stage}-medication-reminder"
  schedule_expression = "rate(1 minute)"
  state               = "ENABLED"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = module.scheduler_lambda.arn
    role_arn = aws_iam_role.scheduler_invoke.arn
    input    = jsonencode({})
  }
}

resource "aws_lambda_permission" "allow_scheduler" {
  statement_id  = "AllowExecutionFromScheduler"
  action        = "lambda:InvokeFunction"
  function_name = module.scheduler_lambda.function_name
  principal     = "scheduler.amazonaws.com"
  source_arn    = aws_scheduler_schedule.medication_reminder.arn
}
