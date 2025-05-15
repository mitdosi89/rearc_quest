terraform{
  required_providers {
    aws = {
      source = "hashicorp/aws"
      }
  }
}

provider "aws" {
  region = "ap-south-1"
  shared_credentials_files = ["C:\\Users\\mitdo\\.aws\\credentials"]
}
