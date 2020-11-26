// DYNAMODB TABLE USED FOR RESERVATIONS
// todo set autoscaling
locals {
  table_name    = "reservations-table"
  hash_key      = "reservation_guid"
  hash_key_type = "S"

  range_key      = "epoch_start"
  range_key_type = "N"

  read_capacity  = 5
  write_capacity = 5

  user_guid_index_name = "UserGUIDIndex"
  user_guid_index_hash = "user_guid"
  user_guid_index_type = "S"
  user_guid_index_proj = "ALL"
  user_guid_index_write = 3
  user_guid_index_read = 3

  ttl_attribute = "TimeToExist"
  ttl_enabled   = false

  billing_mode = "PROVISIONED"
  pitr_enabled = false
}

resource "aws_dynamodb_table" "reservations_table" {
  name           = local.table_name
  hash_key       = local.hash_key
  range_key      = local.range_key
  billing_mode   = local.billing_mode
  read_capacity  = local.read_capacity
  write_capacity = local.write_capacity

  attribute {
    name = local.hash_key
    type = local.hash_key_type
  }

  attribute {
    name = local.range_key
    type = local.range_key_type
  }

  attribute {
    name = local.user_guid_index_hash
    type = local.user_guid_index_type
  }

  global_secondary_index {
    hash_key        = local.user_guid_index_hash
    name            = local.user_guid_index_name
    projection_type = local.user_guid_index_proj
    write_capacity =  local.user_guid_index_write
    read_capacity =  local.user_guid_index_read
  }

  point_in_time_recovery {
    enabled = local.pitr_enabled
  }

  ttl {
    attribute_name = local.ttl_attribute
    enabled        = local.ttl_enabled
  }

  lifecycle {
    ignore_changes = [
      ttl
    ]
  }

  tags = {
    project_name = var.project
    environment  = var.environment
  }
}

output "arn" {
  value = aws_dynamodb_table.reservations_table.arn
}