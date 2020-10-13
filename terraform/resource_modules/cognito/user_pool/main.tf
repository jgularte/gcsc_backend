provider "aws" {
  profile = "default"
  region = var.aws_region
}

resource "aws_cognito_user_pool" "user-pool" {
  name = var.name
  mfa_configuration = var.mfa_config
  username_attributes = var.username_attributes

  auto_verified_attributes = var.auto_verified_attributes

  dynamic "schema" {
    for_each = [for item in var.schema_list: {
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
    reply_to_email_address = var.reply_to
    from_email_address = var.from_email
    email_sending_account = var.sending_account
    source_arn = var.ses_arn
  }

  device_configuration {
    challenge_required_on_new_device = var.challenge_new_device
    device_only_remembered_on_user_prompt = var.device_remembered_prompt
  }

  admin_create_user_config {
    allow_admin_create_user_only = var.admin_create_user
    invite_message_template {
      email_subject = var.admin_email_subject
      email_message = var.admin_body_message
      sms_message = var.admin_body_message
    }
  }

  verification_message_template {
    default_email_option = var.default_email_option
    email_subject = var.email_subject
    email_message = var.email_body
  }

  password_policy {
    minimum_length = var.password_length
    require_lowercase = var.password_lower
    require_numbers = var.password_numbers
    require_uppercase = var.password_upper
    require_symbols = var.password_symbols
    temporary_password_validity_days = var.password_validity
  }

  software_token_mfa_configuration {
    enabled = var.software_tokens
  }

  user_pool_add_ons {
    advanced_security_mode = var.advanced_security
  }

  username_configuration {
    case_sensitive = var.case_sensitive_username
  }
}