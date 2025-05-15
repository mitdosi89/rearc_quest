data "aws_iam_policy_document" "rearc_sqs_s3_queue_policy" {
  statement {
    effect = "Allow"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions   = ["sqs:SendMessage"]
    resources = ["arn:aws:sqs:*:*:${var.sqs_queue_name}"]

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values   = [aws_s3_bucket.rearc_bucket.arn]
    }
  }
}

resource "aws_sqs_queue" "rearc_queue" {
  name   = var.sqs_queue_name
  visibility_timeout_seconds = 120
  policy = data.aws_iam_policy_document.rearc_sqs_s3_queue_policy.json
}

resource "aws_s3_bucket" "rearc_bucket" {
  bucket = var.bucket_name
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.rearc_bucket.id

  queue {
    queue_arn     = aws_sqs_queue.rearc_queue.arn
    events        = ["s3:ObjectCreated:*"]
    filter_prefix = "api_data/"
    filter_suffix = ".json"
  }
}

resource "aws_lambda_event_source_mapping" "event_source_mapping" {
  event_source_arn = aws_sqs_queue.rearc_queue.arn
  enabled          = true
  function_name    = aws_lambda_function.rearc_reporting_lambda.arn
  batch_size       = 1
}