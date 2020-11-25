locals {
  name                     = "GularteCabinSharedCalendarUserPool_sandbox"
  mfa_config               = "OFF"
  username_attributes      = ["email", "phone_number"]
  auto_verified_attributes = ["email"]

  // schema
  schema_list = [
    { data_type = "String", name = "name", required = true },
    { data_type = "String", name = "family_name", required = true },
    { data_type = "String", name = "email", required = true },
    { data_type = "String", name = "phone_number", required = true },
  ]

  // email configuration
  reply_to        = "gulartecabinsharedcalendar@gmail.com"
  from_email      = "gulartecabinsharedcalendar@gmail.com"
  sending_account = "DEVELOPER"

  // todo determine if its worth adding an AWS SES resource to create and destroy this.
  ses_arn = "arn:aws:ses:us-west-2:045526752776:identity/gulartecabinsharedcalendar@gmail.com"

  // device configuration
  challenge_new_device     = false
  device_remembered_prompt = false

  // admin config
  admin_create_user   = true
  admin_email_subject = "Your GularteCabinSharedCalendar temporary password"
  admin_body_message  = "Your username is {username} and temporary password is {####}"

  // verification template
  default_email_option = "CONFIRM_WITH_CODE"
  email_subject        = "Your GularteCabinSharedCalendar verification code"
  email_body           = "Your verification code is {####}"

  // password policy
  password_length   = 8
  password_lower    = true
  password_upper    = true
  password_numbers  = true
  password_symbols  = false
  password_validity = 90

  // software tokens
  software_tokens = false

  // add-ons
  advanced_security = "OFF"

  // username options
  case_sensitive_username = false
}

resource "aws_cognito_user_pool" "user-pool" {
  name = local.name
  mfa_configuration = local.mfa_config
  username_attributes = local.username_attributes

  auto_verified_attributes = local.auto_verified_attributes

  dynamic "schema" {
    for_each = [for item in local.schema_list: {
      data_type = item.data_type
      name = item.name
      required = item.required
    }]

    content {
      attribute_data_type = schema.value.data_type
      name = schema.value.name
      required = schema.value.required
    }
  }

  email_configuration {
    reply_to_email_address = local.reply_to
    from_email_address = local.from_email
    email_sending_account = local.sending_account
    source_arn = local.ses_arn
  }

  device_configuration {
    challenge_required_on_new_device = local.challenge_new_device
    device_only_remembered_on_user_prompt = local.device_remembered_prompt
  }

  admin_create_user_config {
    allow_admin_create_user_only = local.admin_create_user
    invite_message_template {
      email_subject = local.admin_email_subject
      email_message = local.admin_body_message
      sms_message = local.admin_body_message
    }
  }

  verification_message_template {
    default_email_option = local.default_email_option
    email_subject = local.email_subject
    email_message = local.email_body
  }

  password_policy {
    minimum_length = local.password_length
    require_lowercase = local.password_lower
    require_numbers = local.password_numbers
    require_uppercase = local.password_upper
    require_symbols = local.password_symbols
    temporary_password_validity_days = local.password_validity
  }

  software_token_mfa_configuration {
    enabled = local.software_tokens
  }

  user_pool_add_ons {
    advanced_security_mode = local.advanced_security
  }

  username_configuration {
    case_sensitive = local.case_sensitive_username
  }

  tags = {
    project_name = var.project
    environment  = var.environment
  }
}