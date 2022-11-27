terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.38.0"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region = var.aws_region
}

//AWS Lambda
# resource "aws_lambda_layer_version" "lambda-layer" {
#   layer_name          = "selenium-chrome-python3"
#   filename            = "./layers/chrome_headless.zip"
#   compatible_runtimes = ["python3.7", "python3.8"]
# }

data "archive_file" "zip" {
  type        = "zip"
  source_dir  = "../app/src"
  output_path = "fn-moneycontrol-financial-data-scraping.zip"
}

resource "aws_iam_role" "moneycontrol-lambda" {
  name               = "moneycontrol-lambda"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_lambda_function" "moneycontrol" {
  function_name    = "fn-moneycontrol-financial-data-scraping"
  filename         = data.archive_file.zip.output_path
  source_code_hash = data.archive_file.zip.output_base64sha256
  handler          = "function.handler"
  role             = aws_iam_role.moneycontrol-lambda.arn

  runtime = "python3.7"
  layers = [
    "arn:aws:lambda:us-east-1:567944156995:layer:layer_selenium_python:1",
    "arn:aws:lambda:us-east-1:567944156995:layer:layer_chrome_selenium:3"
  ]
}
