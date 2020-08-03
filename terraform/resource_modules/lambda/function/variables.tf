variable "aws_region" {
  type = string
  default = "us-west-2"
  description = "The region in which to build the resource"
}

variable "role_arn" {
  type = string
  description = "IAM Role the lambda should temporarily assume during runtime"
}

variable "function_name" {
  type = string
  description = "Function Name"
}

variable "handler" {
  type = string
  description = "The Entry Point function for the lambda function"
}

variable "timeout" {
  type = number
  description = "The amount of time the lambda is allowed to run, max 900 seconds"
  default = 60
}

variable "memory" {
  type = number
  description = "The amount of memory the lambda is allowed to use"
  default = 256
}

variable "lambda_src_location" {
  type = string
  description = "The local location of the lambda source code"
}

variable "tracing_mode" {
  type = string
  description = "Whether to enable tracing or not, Active or PassThrough"
  default = "PassThrough"
}

variable "environment" {
  type = string
  description = "The runtime environment of the lambda function"
  default = "UNSTATED_ENVIRONMENT"
}