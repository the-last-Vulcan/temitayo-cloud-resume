terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0" # Use a compatible version
    }
  }
  required_version = ">= 1.1.0" # Or your preferred Terraform version
}