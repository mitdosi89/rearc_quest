# resource "aws_lambda_layer_version" "rearc_layer" {
# 	  layer_name       = var.rearc_lambda_layer_name
# 	  s3_bucket        = var.bucket_name
# 	  s3_key           = var.key_rearc_layer_custom
# 	  #source_code_hash = data.archive_file.main.output_base64sha256
	

# 	  compatible_runtimes = ["python3.13","python3.12","python3.11","python3.10","python3.9"]
# 	  depends_on = [
# 	    aws_s3_bucket.rearc_bucket,
# 	  ]
# }
