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
    source                 = "github.com/NHSDigital/api-platform-service-module.git?ref=AMB-52-monitoring-and-alerting-with-statuscake"
  name                     = "personal-demographics"
  path                     = "personal-demographics"
  apigee_environment       = var.apigee_environment
  proxy_type               = (var.force_sandbox || length(regexall("sandbox", var.apigee_environment)) > 0) ? "sandbox" : "live"
  namespace                = var.namespace
  make_api_product         = !(length(var.namespace) > 0 || length(regexall("sandbox", var.apigee_environment)) > 0)
  api_product_display_name = "Personal Demographics Service"
  api_product_description  = ""
  status_cake_username = var.status_cake_username
  status_cake_api_key = var.status_cake_api_key
  status_cake_contact_group = var.status_cake_contact_group
}
