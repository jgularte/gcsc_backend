variable "aws_region" {
  type        = string
  default     = "us-west-2"
  description = "The region in which to build the resource"
}

variable "environment" {
  type        = string
  default     = "prod"
  description = "The production environment of the table"
}

variable "project" {
  type    = string
  default = "GularteCabinSharedCalendarBackend"
}