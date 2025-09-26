terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0" # Use a compatible version
    }
  }
  required_version = ">= 1.1.0" # Or your preferred Terraform version
  backend "gcs" {
    # This must match your GCS bucket for state
    bucket = "eng-diagram-435207-s6-tfstate" # Replace with your actual state bucket name
    prefix = "terraform/state"
  }
}