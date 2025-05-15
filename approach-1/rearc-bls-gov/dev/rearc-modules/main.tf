module "rearc-modules" {
  source        = "../../terraform-modules/rearc-modules"
  bls_gov_function_name = var.bls_gov_function_name
  rearc_bls_gov_url = var.rearc_bls_gov_url
  rearc_reporting_function_name = var.rearc_reporting_function_name
  file_to_fetch = var.file_to_fetch
  sqs_queue_url = var.sqs_queue_url
  sqs_queue_name = var.sqs_queue_name
  bucket_name = var.bucket_name
  rearc_policy_name  = var.rearc_policy_name
  rearc_role_name = var.rearc_role_name
  rearc_dynamodb_tracking_tbl = var.rearc_dynamodb_tracking_tbl
  rearc_key_nation_population_data = var.rearc_key_nation_population_data

}
