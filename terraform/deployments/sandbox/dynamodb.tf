// DYNAMODB TABLE USED FOR RESERVATIONS
module "reservations_table" {
  source         = "../../resource_modules/dynamodb/basic"
  aws_region     = "us-west-2"
  table_name     = "reservations-table_sandbox"
  hash_key       = "reservation_id"
  hash_key_type  = "N"
  range_key      = "start_date_epoch"
  range_key_type = "N"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5
  environment    = "sandbox"
  pitr_enabled   = false
}