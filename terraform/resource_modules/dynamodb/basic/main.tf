provider "aws" {
  profile = "personal"
  region = var.aws_region
}

resource "aws_dynamodb_table" "basic_table" {
  name = var.table_name
  hash_key = var.hash_key
  range_key = var.range_key
  billing_mode = var.billing_mode
  read_capacity = var.read_capacity
  write_capacity = var.write_capacity

  attribute {
    name = var.hash_key
    type = var.hash_key_type
  }

  attribute {
    name = var.range_key
    type = var.range_key_type
  }

  point_in_time_recovery {
    enabled = var.pitr_enabled
  }

  tags = {
    project_name = "GularteCabinSharedCalendar"
    environment = var.environment
  }
}

output "arn" {
  value = aws_dynamodb_table.basic_table.arn
}