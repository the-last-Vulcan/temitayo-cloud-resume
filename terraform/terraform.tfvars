# terraform.tfvars

# Your Google Cloud Project ID.
# This is the unique identifier of your GCP project (e.g., "my-awesome-resume-project-12345").
# You can find this in the GCP Console Dashboard.
gcp_project_id = "eng-diagram-435207-s6" # REPLACE THIS with your actual Project ID from GCP Console

# The GCP region where your Cloud Run service and Firestore database will be deployed.
# Examples: "us-central1", "europe-west1", "asia-northeast1".
# Choose a region geographically close to your target users.
gcp_region = "us-central1" # REPLACE THIS with your desired GCP region

# The specific location ID for your Firestore database.
# This should correspond to your chosen `gcp_region`.
# Examples: "nam5" for us-central1, "eur3" for europe-west1, "asia-northeast1" for asia-northeast1.
# Firestore locations are specific; check Firestore documentation for exact mapping.
firestore_location = "us-central1" # REPLACE THIS with the correct Firestore location for your chosen region

# The tag of the container image for your Cloud Run service.
# This will be the full tag from your Google Container Registry, e.g.,
# "gcr.io/your-project-id/visitor-counter:f376aeae01c2e268770ac9aafeba6df6ef2764fb"
# You'll get this from your Cloud Build output (it's the `:f376aeae01c2e268770ac9aafeba6df6ef2764fb` part from your last build tag).
#cloud_run_image_tag = "latest" # REPLACE THIS with the actual tag from your successful Cloud Build

# The name of the GCS bucket for your website's static files.
# This name MUST BE GLOBALLY UNIQUE across all of Google Cloud.
# If you plan to use a custom domain (e.g., www.yourdomain.com), this bucket name should ideally match your domain.
gcs_bucket_name = "www.temitayoapata.online" # REPLACE THIS with your desired, globally unique GCS bucket name

# The location for your GCS bucket.
# For static websites, it's recommended to use a multi-region location for high availability.
# Examples: "US" (for multi-region in the US), "EUROPE", "ASIA".
gcs_bucket_location = "US-CENTRAL1" # REPLACE THIS with your desired multi-region location

# Variables with default values (you only need to uncomment and change if you want to override the default)
# cloud_run_service_name       = "visitor-counter"
# cloud_run_service_account_id = "visitor-counter-sa"