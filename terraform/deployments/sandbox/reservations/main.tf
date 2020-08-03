module "reservations_table" {
  source = "../../../resource_modules/dynamodb/basic"
  aws_region = "us-west-2"
  table_name = "reservations-table_sandbox"
  hash_key = "created_by"
  hash_key_type = "S"
  range_key = "start_date_epoch"
  range_key_type = "N"
  billing_mode = "PROVISIONED"
  read_capacity = 5
  write_capacity = 5
  environment = "sandbox"
  pitr_enabled = false
  ttl_att_name = ""
}

module "reservations_lambda_role" {
  source = "../../../resource_modules/iam/role"
  aws_region = "us-west-2"
  role_name = "reservations-lambda-role_sandbox"
  environment = "sandbox"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": "test"
    }
  ]
}
EOF

  iam_policy_name = "reservations-lambda-iam-policy_sandbox"
  iam_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:BatchGetItem",
        "dynamodb:BatchWriteItem",
        "dynamodb:DeleteItem",
        "dynamodb:PutItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:Update"
      ],
      "Effect": "Allow",
      "Resource": "${module.reservations_table.arn}"
    }
  ]
}
EOF
}

terraform {
  backend "s3" {
    bucket = "gulartecabincalendarterraform"
    key = "reservations-sandbox"
    region = "us-west-2"
  }
}