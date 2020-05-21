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

variable "status_cake_username" {
    type = string
    description = "Statuscake username for monitoring and alerting"
}

variable "status_cake_api_key" {
    type = string
    description = "Statuscake apikey for monitoring and alerting"
}

variable "status_cake_contact_group" {
    type = string
    description = "Statuscake Contact Group for monitoring and alerting"
}

// FIXME: remove it
variable "covid-19-testing-channel-availability-host" {
    type = string
    description = "Ignore"
    default = ""
}
