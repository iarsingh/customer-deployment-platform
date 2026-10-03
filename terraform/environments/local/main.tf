terraform {
  required_version = ">= 1.5.0"
}

module "billing_callback" {
  source      = "../../modules/service"
  name        = "billing-callback"
  team        = "payments"
  environment = "dev"
}

output "namespace" {
  value = module.billing_callback.namespace
}

output "labels" {
  value = module.billing_callback.labels
}

output "resources" {
  value = module.billing_callback.resources
}
