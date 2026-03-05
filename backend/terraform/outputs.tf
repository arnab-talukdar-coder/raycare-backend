output "api_endpoint" {
  value = module.http_api.api_endpoint
}

output "medical_records_bucket" {
  value = aws_s3_bucket.medical_records.id
}

output "dynamodb_tables" {
  value = local.table_names
}
