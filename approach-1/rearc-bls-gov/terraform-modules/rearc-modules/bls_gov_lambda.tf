data "archive_file" "bls_gov_archieve" {
  type        = "zip"
  source_file = "${path.module}/bls_gov_processing.py"
  output_path = "bls_lambda_function_payload.zip"
}

resource "aws_lambda_function" "bls_gov_lambda" {
  filename      = data.archive_file.bls_gov_archieve.output_path
  function_name = var.bls_gov_function_name
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "bls_gov_processing.lambda_handler"
  layers      = ["arn:aws:lambda:ap-south-1:815931044416:layer:v2-integration-rearc-python-request:6","arn:aws:lambda:ap-south-1:336392948345:layer:AWSSDKPandas-Python313:1"]
  timeout = 300

  source_code_hash = data.archive_file.bls_gov_archieve.output_base64sha256

  runtime = "python3.13"

  environment {
    variables = {
      BUCKET_NAME = "${var.bucket_name}",
      REARC_URL = "${var.rearc_bls_gov_url}"
      TRACKING_TBL = "${var.rearc_dynamodb_tracking_tbl}"
      KEY_NATION_POPULATION_DATA = "${var.rearc_key_nation_population_data}"
      NATION_POPULATION_API_URL = "${var.rearc_nation_population_api_url}"
      USER_AGENT = "${var.rearc_user_agent}"
      CONTENT_TYPE = "${var.rearc_content_type}"
    }
  }
}

