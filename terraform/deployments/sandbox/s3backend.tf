terraform {
  backend "s3" {
    bucket = "gulartecabincalendarterraform"
    key    = "backend-sandbox"
    region = "us-west-2"
  }
}