variable "aws_region" {
  default = "us-west-2"
  type = string
}

variable "schema_list" {
  type = any
  description = "list of schema objects, keeping it simple for now"
}

variable "name" {
  description = "name of the cognito pool"
  type = string
}

variable "mfa_config" {
  type = string
  default = "OFF"
}

variable "username_attributes" {
  type = list(string)
  description = "what type of info can be used as a username"
}

variable "auto_verified_attributes" {
  type = list(string)
  description = "the user attributes that will be automatically verified"
}

variable "reply_to" {
  type = string
  description = "Where replies from users will be sent"
}

variable "from_email" {
  type = string
  description = "FROM title shown in emails sent by account"
}

variable "sending_account" {
  type = string
  description = "Choose a customer developer email or the defualt aws ses option"
}

variable "ses_arn" {
  type = string
  description = "ARN of the SES identity used to send emails"
}

variable "challenge_new_device" {
  type = bool
  description = "whether new user devices need to be mfa challenged"
}

variable "device_remembered_prompt" {
  type = bool
  description = "Don't fully understand this one, setting to false"
}

variable "admin_create_user" {
  type = bool
  description = "Only allow admin to create users"
}

variable "admin_email_subject" {
  type = string
  description = "What to place in email from admin user create subject line"
}

variable "admin_body_message" {
  type = string
  description = "What to place in the sms/email body"
}

variable "default_email_option" {
  type = string
  description = "Whether emails are verified with code or link"
}

variable "email_subject" {
  type = string
  description = "Subject line of user created account"
}

variable "email_body" {
  type = string
  description = "Body of user created account email verification"
}

variable "password_length" {
  type = number
  description = "min length of password"
}

variable "password_lower" {
  type = bool
  description = "does password require lowercase"
}

variable "password_upper" {
  type = bool
  description = "does password require uppercase"
}

variable "password_numbers" {
  type = bool
  description = "does password require numbers"
}

variable "password_symbols" {
  type = bool
  description = "does password require symbols"
}

variable "password_validity" {
  type = number
  description = "how long the temp password set by admin is valid"
}

variable "software_tokens" {
  type = bool
  description = "whether users can get software tokens for auth"
}

variable "advanced_security" {
  type = string
  description = "Whether aws will enable advanced security"
}

variable "case_sensitive_username" {
  type = bool
  description = "is the username case sensitive during login"
}


