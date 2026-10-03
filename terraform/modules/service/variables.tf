variable "name" {
  type = string
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,30}$", var.name)) && !endswith(var.name, "-")
    error_message = "name must match the platform API rule."
  }
}

variable "team" {
  type = string
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,30}$", var.team)) && !endswith(var.team, "-")
    error_message = "team must match the platform API rule."
  }
}

variable "environment" {
  type = string
  validation {
    condition     = contains(["dev", "staging"], var.environment)
    error_message = "prod is not a self-serve environment. Promote through GitOps."
  }
}

variable "cpu_request" {
  type    = string
  default = "100m"
}

variable "memory_request" {
  type    = string
  default = "128Mi"
}

variable "cpu_limit" {
  type    = string
  default = "500m"
}

variable "memory_limit" {
  type    = string
  default = "256Mi"
}
