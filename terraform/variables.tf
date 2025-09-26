variable "gcp_project_id" {
  description = "The GCP project ID."
  type        = string
}

variable "gcp_region" {
  description = "The GCP region for Cloud Run and Firestore (e.g., us-central1)."
  type        = string
}

variable "firestore_location" {
  description = "The location for your Firestore database (e.g., nam5 for us-central1)."
  type        = string
}

variable "cloud_run_service_name" {
  description = "The name for your Cloud Run service."
  type        = string
  default     = "visitor-counter"
}

variable "cloud_run_image_tag" {
  description = "The tag of the container image for Cloud Run (e.g., 'latest' or a specific SHA)."
  type        = string
}

variable "cloud_run_service_account_id" {
  description = "The ID for the Cloud Run service account (e.g., 'visitor-counter-sa')."
  type        = string
  default     = "visitor-counter-sa"
}

variable "gcs_bucket_name" {
  description = "The name of the GCS bucket for your website (e.g., www.yourdomain.com)."
  type        = string
}

variable "gcs_bucket_location" {
  description = "The location for your GCS bucket (must be a multi-region for static websites, e.g., 'US', 'EUROPE')."
  type        = string
}