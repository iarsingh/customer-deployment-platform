output "labels" {
  value = local.labels
}

output "resources" {
  value = local.resources
}

output "namespace" {
  value = "${var.team}-${var.environment}"
}
