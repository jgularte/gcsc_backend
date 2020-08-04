// REMEMBER TO: 'export AWS_PROFILE=personal'

// DYNAMODB TABLE USED FOR RESERVATIONS
module "reservations_table" {
  source = "../../../resource_modules/dynamodb/basic"
  aws_region = "us-west-2"
  table_name = "reservations-table_sandbox"
  hash_key = "reservation_id"
  hash_key_type = "N"
  range_key = "start_date_epoch"
  range_key_type = "N"
  billing_mode = "PROVISIONED"
  read_capacity = 5
  write_capacity = 5
  environment = "sandbox"
  pitr_enabled = false
}

// IAM ROLE THAT WILL BE GIVEN TO THE RESERVATIONS LAMBDA FUNCTION
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
        "dynamodb:UpdateItem",
        "xray:*"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

// PERFORM DOS2UNIX CALL ON DEPLOY SCRIPT, LESS ANNOYING THIS WAY
resource "null_resource" "dos2unix" {
  provisioner "local-exec" {
    command = "dos2unix create-reservations.sh"
    working_dir = "../../../scripts"
  }
}

// SCRIPT TO PACKAGE LAMBDA BEFORE DEPLOYMENT
// FIRST PARAM: Script Location
// SECOND PARAM: Environment
// THIRD PARAM: MODULE TO DEPLOY
// FOURTH PARAM: Source Code Location
data "external" "create_reservation_lambda" {
  program = ["../../../scripts/create-reservations.sh", "sandbox", "reservations", "../../../../"]
}

// RESERVATIONS LAMBDA FUNCTION
module "reservations-lambda-function" {
  source = "../../../resource_modules/lambda/function"
  role_arn = module.reservations_lambda_role.role_arn
  function_name = "reservations-lambda_sandbox"
  aws_region = "us-west-2"
  handler = "reservations.handler"
  timeout = 30
  memory = 256
  lambda_src_location = "${data.external.create_reservation_lambda.result.package_loc}/lambda.zip"
  environment = "sandbox"
  tracing_mode = "Active"
}

terraform {
  backend "s3" {
    bucket = "gulartecabincalendarterraform"
    key = "reservations-sandbox"
    region = "us-west-2"
  }
}