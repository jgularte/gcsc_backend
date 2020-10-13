provider "aws" {
  region = var.aws_region
}

resource "aws_iam_role" "role" {
  name = var.role_name
  assume_role_policy = var.assume_role_policy

  tags = {
    project_name = "GularteCabinSharedCalendar"
    environment = var.environment
  }
}

resource "aws_iam_policy" "policy" {
  name = var.iam_policy_name
  policy = var.iam_policy
}

resource "aws_iam_role_policy_attachment" "attach" {
  policy_arn = aws_iam_policy.policy.arn
  role = aws_iam_role.role.name
}

output "role_arn" {
  value = aws_iam_role.role.arn
}