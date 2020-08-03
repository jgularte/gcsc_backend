variable "aws_region" {
  type = string
  default = "us-west-2"
  description = "The region in which to build the resource"
}

variable "table_name" {
  type = string
  description = "name of the table"
}

variable "hash_key" {
  description = "The hash key to be used for the table"
}

variable "hash_key_type" {
  type = string
  description = "The variable type for the hash key"
}

variable "range_key" {
  description = "The range key to be used for the table"
}

variable "range_key_type" {
  type = string
  description = "The variable type for the range key"
}

variable "read_capacity" {
  type = number
  default = 5
}

variable "write_capacity" {
  type = number
  default = 5
}

variable "billing_mode" {
  type = string
  default = "PROVISIONED"
}

variable "ttl_att_name" {
  type = string
  default = "TimeToExist"
}

variable "ttl_enabled" {
  type = bool
  default = false
}

variable "pitr_enabled" {
  type = bool
  default = false
}

variable "environment" {
  type = string
  default = "UNSTATED_ENVIRONMENT"
  description = "The production environment of the table"
}