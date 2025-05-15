data "aws_iam_policy_document" "rearc_assume_role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_policy" "rearc_s3_policy" {
  name        = var.rearc_s3_policy_name
  description = "custom s3 policy"
  policy = file("${path.module}/s3_policy.json")
}

resource "aws_iam_policy" "rearc_cloudwatch_policy" {
  name        = var.rearc_cloudwatch_policy_name
  description = "custom cloudwatch policy"
  policy = file("${path.module}/cloudwatch_policy.json")
}

resource "aws_iam_policy" "rearc_sqs_policy" {
  name        = var.rearc_sqs_policy_name
  description = "custom sqs policy"
  policy = file("${path.module}/sqs_policy.json")
}

resource "aws_iam_policy" "rearc_dynamodb_policy" {
  name        = var.rearc_dynamodb_policy_name
  description = "custom dynamodb policy"
  policy = file("${path.module}/dynamodb_policy.json")
}

resource "aws_iam_role" "iam_for_lambda" {
  name                = var.rearc_role_name
  assume_role_policy  = data.aws_iam_policy_document.rearc_assume_role.json
  managed_policy_arns = [aws_iam_policy.rearc_s3_policy.arn,aws_iam_policy.rearc_cloudwatch_policy.arn,aws_iam_policy.rearc_dynamodb_policy.arn,aws_iam_policy.rearc_sqs_policy.arn]
}