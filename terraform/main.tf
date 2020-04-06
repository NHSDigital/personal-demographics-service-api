provider "apigee" {
  org          = var.apigee_organization
  access_token = var.apigee_token
}

terraform {
  backend "azurerm" {}

  required_providers {
    apigee = "~> 0.0"
    archive = "~> 1.3"
  }
}


module "personal-demographics-service" {
  source             = "github.com/NHSDigital/api-platform-service-module?ref=apm-501-change-proxy-location"
  name               = "personal-demographics"
  path               = "personal-demographics"
  apigee_environment = var.apigee_environment
  proxy_type         = length(regexall("sandbox", var.apigee_environment)) > 0 ? "sandbox" : "live"
}
