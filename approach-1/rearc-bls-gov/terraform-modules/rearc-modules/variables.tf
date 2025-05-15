variable "bls_gov_function_name" {
  type    = string
  default = "default_bls_gov_function_name"
}

variable "rearc_reporting_function_name" {
  type    = string
  default = "default_rearc_reporting_function_name"
}

variable "rearc_role_name" {
  type    = string
  default = "default_rearc_role_name"
}


# variable "rearc_lambda_layer_name" {
#   type    = string
#   default = "default_rearc_lambda_layer_name"
# }


variable "rearc_managed_pandas_layer" {
  type    = string
  default = "default_rearc_managed_pandas_layer"
}


variable "key_rearc_layer_custom" {
  type    = string
  default = "default_key_rearc_layer_custom"
}


variable "rearc_policy_name" {
  type    = string
  default = "default_rearc_policy_name"
}

variable "bucket_name" {
  type    = string
  default = "default_bucket_name"
}

variable "rearc_dynamodb_tracking_tbl" {
  type    = string
  default = "default_rearc_dynamodb_tracking_tbl"
}

variable "rearc_bls_gov_url" {
  type    = string
  default = "default_rearc_bls_gov_url"
}

variable "file_to_fetch" {
  type    = string
  default = "default_file_to_fetch"
}

variable "sqs_queue_url" {
  type    = string
  default = "default_sqs_queue_url"
}

variable "sqs_queue_name" {
  type    = string
  default = "default_sqs_queue_name"
}

variable "rearc_s3_policy_name" {
  type    = string
  default = "default_rearc_s3_policy_name"
}

variable "rearc_cloudwatch_policy_name" {
  type    = string
  default = "default_rearc_cloudwatch_policy_name"
}

variable "rearc_sqs_policy_name" {
  type    = string
  default = "default_rearc_sqs_policy_name"
}

variable "rearc_dynamodb_policy_name" {
  type    = string
  default = "default_rearc_dynamodb_policy_name"
}

variable "rearc_key_nation_population_data" {
  type    = string
  default = "default_rearc_key_nation_population_data"
}

variable "rearc_nation_population_api_url" {
  type    = string
  default = "default_rearc_nation_population_api_url"
}

variable "rearc_user_agent" {
  type    = string
  default = "default_rearc_user_agent"
}

variable "rearc_content_type" {
  type    = string
  default = "default_rearc_content_type"
}