// DYNAMODB TABLE USED FOR USER PROFILE INFO
// todo set autoscaling
resource "aws_dynamodb_table" "user_info_table" {
  name           = "userinfo-table_sandbox"
  hash_key       = "user_guid"
  billing_mode   = "PROVISIONED"
  read_capacity  = 3
  write_capacity = 3

  attribute {
    name = "user_guid"
    type = "S"
  }

  point_in_time_recovery {
    enabled = false
  }

  ttl {
    attribute_name = "TimeToExist"
    enabled        = false
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

output "userinfo_db_arn" {
  value = aws_dynamodb_table.user_info_table.arn
}