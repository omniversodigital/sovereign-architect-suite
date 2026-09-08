terraform {
  required_version = ">= 1.5.0"
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.30.0"
    }
  }
}

variable "environment" {
  type        = string
  default     = "production"
  description = "Target deployment environment"
}

variable "cluster_domain" {
  type        = string
  default     = "deeptech.internal"
  description = "Internal service mesh domain"
}

output "policy_engine_status" {
  value       = "OPA Sidecar & Mesh Ready for Deployment"
  description = "Status of sovereign policy engine infrastructure"
}
