module "main-user-pool" {
  source = "../../../resource_modules/cognito/user_pool"
  name = "GularteCabinSharedCalendarUserPool"
  mfa_config = "OFF"
  username_attributes = ["email", "phone_number"]
  auto_verified_attributes = ["email"]

  // schema
  schema_list = [
    {data_type = "String", name = "name", required = true},
    {data_type = "String", name = "family_name", required = true},
    {data_type = "String", name = "email", required = true},
    {data_type = "String", name = "phone_number", required = true},
  ]

  // email configuration
  reply_to = "gulartecabinsharedcalendar@gmail.com"
  from_email = "gulartecabinsharedcalendar@gmail.com"
  sending_account = "DEVELOPER"

  // todo determine if its worth adding an AWS SES resource to create and destroy this.
  ses_arn = "arn:aws:ses:us-west-2:045526752776:identity/gulartecabinsharedcalendar@gmail.com"

  // device configuration
  challenge_new_device = false
  device_remembered_prompt = false

  // admin config
  admin_create_user = true
  admin_email_subject = "Your GularteCabinSharedCalendar temporary password"
  admin_body_message = "Your username is {username} and temporary password is {####}"

  // verification template
  default_email_option = "CONFIRM_WITH_CODE"
  email_subject = "Your GularteCabinSharedCalendar verification code"
  email_body = "Your verification code is {####}"

  // password policy
  password_length = 8
  password_lower = true
  password_upper = true
  password_numbers = true
  password_symbols = false
  password_validity = 90

  // software tokens
  software_tokens = false

  // add-ons
  advanced_security = "OFF"

  // username options
  case_sensitive_username = false
}

terraform {
  backend "s3" {
    bucket = "gulartecabincalendarterraform"
    key = "cognito-user-pool-sandbox"
    region = "us-west-2"
  }
}