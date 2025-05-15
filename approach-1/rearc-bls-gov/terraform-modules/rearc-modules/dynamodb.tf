resource "aws_dynamodb_table" "rearc-dynamodb-table" {
  name           = var.rearc_dynamodb_tracking_tbl
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "date_time"

  attribute {
    name = "date_time"
    type = "S"
  }
  
}