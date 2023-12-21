terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-2"
  access_key = var.aws_access_key_id
  secret_key = var.aws_secret_access_key
}

# RSA key of size 4096 bits
resource "tls_private_key" "terraform_rsa_4096" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

variable "key_name" {}

resource "aws_key_pair" "key_pair" {
  key_name   = var.key_name
  public_key = tls_private_key.terraform_rsa_4096.public_key_openssh
}

resource "local_file" "private_key" {
  content = tls_private_key.terraform_rsa_4096.private_key_pem
  filename = var.key_name
}