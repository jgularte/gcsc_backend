terraform {
  backend "s3" {
    bucket = "gulartecabincalendarterraform"
    key    = "backend"
    region = "us-west-2"
  }
}