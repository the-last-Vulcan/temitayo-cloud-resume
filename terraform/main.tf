# terraform/main.tf

# Terraform backend configuration in versions.tf

# Configure the Google Cloud provider
provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

# --- Cloud Run Service ---
resource "google_cloud_run_service" "visitor_counter_service" {
  name     = var.cloud_run_service_name
  location = var.gcp_region

  template {
    spec {
      service_account_name = google_service_account.cloud_run_sa.email # Link to the SA defined below
      containers {
        image = "gcr.io/${var.gcp_project_id}/${var.cloud_run_service_name}:${var.cloud_run_image_tag}"
        # No 'env' block for PORT here anymore!
      }
    }
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "0" # Keep 0 to prevent excess billing
        "autoscaling.knative.dev/maxScale" = "5"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Allow unauthenticated invocations for Cloud Run (public access)
resource "google_cloud_run_service_iam_member" "visitor_counter_public_access" {
  location = google_cloud_run_service.visitor_counter_service.location
  project  = google_cloud_run_service.visitor_counter_service.project
  service  = google_cloud_run_service.visitor_counter_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}


# --- Firestore Database ---
resource "google_firestore_database" "default_database" {
  project     = var.gcp_project_id
  name        = "(default)" # Use the default Firestore database
  location_id = var.firestore_location # e.g., "nam5" for us-central1
  type        = "FIRESTORE_NATIVE"
}

# --- Service Account for Cloud Run ---
resource "google_service_account" "cloud_run_sa" {
  account_id   = var.cloud_run_service_account_id
  display_name = "Service Account for Cloud Run backend"
  project      = var.gcp_project_id
}

# IAM bindings for the Cloud Run Service Account
resource "google_project_iam_member" "cloud_run_firestore_access" {
  project = var.gcp_project_id
  role    = "roles/datastore.user" # Firestore uses datastore roles for write access
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_project_iam_member" "cloud_run_cloud_build_access" {
  project = var.gcp_project_id
  role    = "roles/cloudbuild.builds.viewer" # Or Cloud Build Service Account if needed for complex builds
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# You might need other roles depending on your exact backend needs,
# such as 'roles/serviceusage.serviceUsageConsumer' for the SA itself.
resource "google_project_iam_member" "cloud_run_service_usage_consumer" {
  project = var.gcp_project_id
  role    = "roles/serviceusage.serviceUsageConsumer"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# --- Google Cloud Storage Bucket for Frontend ---
# This assumes your bucket is named after your domain, e.g., www.temitayoapata.online
resource "google_storage_bucket" "website_bucket" {
  name          = var.gcs_bucket_name
  location      = var.gcs_bucket_location # Must be multi-region for static website hosting (e.g., "US")
  uniform_bucket_level_access = true # Recommended for security

  website {
    main_page_suffix = "index.html"
    not_found_page   = "404.html" # Optional, define your 404 page
  }
}

# Make the bucket publicly readable for static website hosting
resource "google_storage_bucket_iam_member" "website_bucket_public_access" {
  bucket = google_storage_bucket.website_bucket.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

# --- Enable necessary APIs (if not already enabled) ---
resource "google_project_service" "cloud_run_api" {
  project = var.gcp_project_id
  service = "run.googleapis.com"
  disable_on_destroy = false # Set to true if you want to disable on terraform destroy
}

resource "google_project_service" "firestore_api" {
  project = var.gcp_project_id
  service = "firestore.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "cloud_build_api" {
  project = var.gcp_project_id
  service = "cloudbuild.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "artifact_registry_api" {
  project = var.gcp_project_id
  service = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

