variable "function_name" {
  type = string
}

variable "source_dir" {
  type = string
}

variable "output_path" {
  type = string
}

variable "handler" {
  type = string
}

variable "role_arn" {
  type = string
}

variable "runtime" {
  type    = string
  default = "python3.12"
}

variable "timeout" {
  type    = number
  default = 30
}

variable "memory_size" {
  type    = number
  default = 512
}

variable "environment" {
  type    = map(string)
  default = {}
}

variable "layers" {
  type    = list(string)
  default = []
}
