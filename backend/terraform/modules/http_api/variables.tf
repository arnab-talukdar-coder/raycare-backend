variable "name" {
  type = string
}

variable "stage_name" {
  type    = string
  default = "$default"
}

variable "lambdas" {
  type = map(string)
}

variable "route_to_lambda" {
  type = map(string)
}
