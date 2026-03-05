variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "project_name" {
  type    = string
  default = "raycare"
}

variable "stage" {
  type    = string
  default = "prod"
}

variable "jwt_secret" {
  type      = string
  sensitive = true
}

variable "medical_records_bucket" {
  type    = string
  default = "raycare-medical-records"
}

variable "dependency_layer_arn" {
  type    = string
  default = ""
}
