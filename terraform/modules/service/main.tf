terraform {
  required_version = ">= 1.5.0"
}

locals {
  labels = {
    app         = var.name
    team        = var.team
    environment = var.environment
    managed-by  = "meridian-platform"
  }
  resources = {
    requests = {
      cpu    = var.cpu_request
      memory = var.memory_request
    }
    limits = {
      cpu    = var.cpu_limit
      memory = var.memory_limit
    }
  }
}
