variable "apigee_organization" {
  type = string
  description = "ID of the apigee org to deploy to."
}

variable "apigee_environment" {
  type = string
  description = "ID of the apigee environment to deploy to"
}

variable "apigee_token" {
  type = string
  description = "Apigee OAuth Access Token."
}

variable "namespace" {
  type = string
  description = "Namespace to deploy proxies etc. in to, for canaries or deploys. To make it prettier, start with a hyphen (e.g. '-apm-123')."
  default = ""
}

variable "force_sandbox" {
  type = bool
  description = "Force a sandbox deploy instead of trying to detect if the deploy is happenning in a sandbox env"
  default = false
}
