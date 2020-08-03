variable "aws_region" {
  type = string
  default = "us-west-2"
  description = "The region in which to build the resource"
}

variable "effect" {
  type = string
  default = "Allow"
  description = "The effect the policy document will have. Allow or x"
}

variable "assume_role_policy" {
  description = "the JSON policy to use for the assumed role"
}

variable "iam_policy" {
  description = "the JSON iam role policy."
}

variable "iam_policy_name" {
  type = string
  description = "the name of the policy to be attached to the role"
}

variable "role_name" {
  type = string
  description = "The name of the iam role"
}

variable "environment" {
  type = string
  description = "The runtime environment for the policy"
  default = "UNSTATED_ENVIRONMENT"
}