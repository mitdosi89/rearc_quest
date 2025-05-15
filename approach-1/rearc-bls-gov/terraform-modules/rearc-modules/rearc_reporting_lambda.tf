data "archive_file" "rearc_reporting_archieve" {
  type        = "zip"
  source_file = "${path.module}/rearc_reporting_processing.py"
  output_path = "rearc_reporting_function_payload.zip"
}

resource "aws_lambda_function" "rearc_reporting_lambda" {
  filename      = data.archive_file.rearc_reporting_archieve.output_path
  function_name = var.rearc_reporting_function_name
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "rearc_reporting_processing.lambda_handler"
  layers      = ["arn:aws:lambda:ap-south-1:336392948345:layer:AWSSDKPandas-Python313:1"]
  timeout = 120
  #timeout = 30

  source_code_hash = data.archive_file.rearc_reporting_archieve.output_base64sha256

  runtime = "python3.13"

  environment {
    variables = {
      BUCKET_NAME = "${var.bucket_name}",
      FILE_TO_FETCH = "${var.file_to_fetch}"
      SQS_QUEUE_URL = "${var.sqs_queue_url}"
      TRACKING_TBL = "${var.rearc_dynamodb_tracking_tbl}"
    }
  }
}

