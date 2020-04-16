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
  source                   = "github.com/NHSDigital/api-platform-service-module?ref=apm-634-update-api-product"
  name                     = "personal-demographics"
  path                     = "personal-demographics"
  apigee_environment       = var.apigee_environment
  proxy_type               = length(regexall("sandbox", var.apigee_environment)) > 0 ? "sandbox" : "live"
  namespace                = var.namespace
  make_api_product         = length(var.namespace) > 0 ? false : true
  api_product_display_name = "Personal Demographics Service"
  api_product_description  = "TODO: Link to docs?"
}
