output "cloud_run_service_url" {
  description = "The URL of the deployed Cloud Run service."
  value       = google_cloud_run_service.visitor_counter_service.status[0].url
}

# output "gcs_bucket_url" {
#   description = "The URL of the GCS website bucket."
#   value       = "https://${google_storage_bucket.website_bucket.name}"
# }

output "cloud_run_service_account_email" {
  description = "The email of the Cloud Run service account."
  value       = google_service_account.cloud_run_sa.email
}