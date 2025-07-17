Here's a comprehensive README.md for your Cloud Resume Challenge project, incorporating details from your files and our discussions:

Cloud Resume Challenge - Temitayo's Portfolio
This repository hosts the infrastructure and application code for Temitayo's Cloud Resume Challenge, a modern, serverless web application designed to showcase cloud development skills. The project leverages Google Cloud Platform (GCP) for all its services and automates deployments using Terraform and GitHub Actions.

Table of Contents
Project Overview

Architecture

Features

Prerequisites

Local Development

Deployment (CI/CD)

Monitoring & Logging

Security Considerations

Contributing

License

1. Project Overview
The Cloud Resume Challenge is a hands-on project that demonstrates proficiency in cloud technologies, DevOps practices, and web development. This implementation uses GCP's serverless offerings to create a scalable, cost-effective, and highly available online resume with a unique visitor counter.

2. Architecture
The architecture is entirely serverless on Google Cloud Platform, providing high scalability and minimal operational overhead.

Frontend: A static HTML/CSS/JavaScript website hosted on a Google Cloud Storage (GCS) bucket.

CDN: Cloudflare is used as the Content Delivery Network (CDN) to cache the frontend content globally, improving load times and reducing latency for users worldwide.

Backend API: A Python Flask API deployed as a Google Cloud Run service. This API handles the visitor count logic.

Database: Google Cloud Firestore (Native mode) is used as the NoSQL database to store and manage the visitor count.

Infrastructure as Code (IaC): All GCP resources are defined and managed using Terraform.

CI/CD: GitHub Actions automate the testing, building, and deployment processes for both frontend and backend.

Architecture Diagram (Conceptual)
+----------------+      +------------------+      +---------------------+
|   End User     |----->|     Cloudflare   |----->|   GCS Bucket        |
|                |      |     (CDN/DNS)    |      | (Static Frontend)   |
+----------------+      +------------------+      +---------------------+
                                 ^
                                 | HTTP(S) Request for API
                                 |
+----------------+      +---------------------+      +-----------------+
|   Web Frontend |----->|  Cloud Run Service  |----->|     Firestore   |
| (JS Fetch API) |      | (Python Flask API)  |      |   (Visitor Count) |
+----------------+      +---------------------+      +-----------------+
3. Features
Serverless Frontend: Static website hosted on GCS for high availability and low cost.

Scalable Backend: Cloud Run automatically scales the API based on demand.

Real-time Visitor Counter: Tracks and displays the number of visitors using Firestore.

Automated Infrastructure: Terraform manages all GCP resources, ensuring consistency and reproducibility.

Continuous Integration & Deployment (CI/CD):

Backend: Automated testing, Docker image build, push to Artifact Registry, and Cloud Run deployment on code pushes.

Frontend: Automatic synchronization of website files to GCS bucket on code pushes.

Cache Invalidation: Automated cache purging in Cloudflare after frontend deployments to ensure immediate content updates.

Secure Authentication: GitHub Actions use Workload Identity Federation (OIDC) for secure, keyless authentication to GCP during CI/CD.

4. Prerequisites
To set up and deploy this project, you will need:

Google Cloud Platform (GCP) Account: With billing enabled.

GitHub Account: To host the repository and use GitHub Actions.

Cloudflare Account: With a registered domain and configured DNS pointing to your GCS bucket.

gcloud CLI: Installed and authenticated locally.

terraform CLI: Installed locally (version 1.8.x recommended).

Python 3.11+: Installed locally for backend development.

pip and pytest: For managing Python dependencies and running tests.

5. Local Development
5.1. Backend (Python Flask API)
Navigate to the backend directory:

Bash

cd counter_backend
Install dependencies:

Bash

pip install -r requirements.txt
Run tests:

Bash

pytest
Run the Flask application locally:

Bash

python main.py
The API should be available at http://127.0.0.1:8080 (or as configured in main.py).

5.2. Frontend (Static Website)
Navigate to the frontend directory:

Bash

cd frontend # (Assuming your frontend files are in a 'frontend' folder, otherwise it's your repo root)
Open index.html in your web browser.

Modify main.js to point to your local backend API endpoint for testing purposes.

6. Deployment (CI/CD)
The project leverages GitHub Actions for automated CI/CD.

6.1. Initial Setup (Terraform)
IMPORTANT: Before your first CI/CD run, ensure your GCP project is set up and essential services are enabled. Some of these are managed by Terraform, but manual setup for the state bucket and service account for GitHub Actions is necessary.

Clone the repository:

Bash

git clone https://github.com/your-username/temitayo-cloud-resume.git
cd temitayo-cloud-resume
Navigate to the terraform directory:

Bash

cd terraform
Configure terraform.tfvars:
Rename terraform.tfvars.example to terraform.tfvars and fill in your specific GCP project ID, regions, bucket names, and Cloudflare details:

Terraform

gcp_project_id      = "eng-diagram-435207-s6"
gcp_region          = "us-central1"
firestore_location  = "us-central1" # Must match existing Firestore location
gcs_bucket_name     = "www.temitayoapata.online"
gcs_bucket_location = "US-CENTRAL1" # Must match existing GCS bucket location
# cloud_run_image_tag and other variables will be handled by CI/CD
Note: cloud_run_image_tag will be dynamically passed by GitHub Actions during deployment.

Backend State Configuration (Manual One-Time Setup in GCP):

Create a GCS bucket in your GCP project to store Terraform state (e.g., gs://eng-diagram-435207-s6-tfstate).

Your main.tf should already define this backend:

Terraform

terraform {
  backend "gcs" {
    bucket = "eng-diagram-435207-s6-tfstate" # Your state bucket name
    prefix = "terraform/state"
  }
}
Initialize Terraform:

Bash

terraform init
Import Existing Resources (Crucial for first-time setup):
Since some resources might have been manually created or you're taking over existing infrastructure, you need to import them into Terraform state.

GCS Website Bucket:

Bash

terraform import google_storage_bucket.website_bucket www.temitayoapata.online
GCS Public Access IAM Member: (After ensuring allUsers only has Storage Object Viewer role in console)

Bash

terraform import google_storage_bucket_iam_member.website_bucket_public_access "www.temitayoapata.online/roles/storage.objectViewer/allUsers"
Firestore Default Database: (Ensure your PowerShell is properly quoting the ID)

Bash

terraform import google_firestore_database.default_database "projects/eng-diagram-435207-s6/databases/(default)"
You might need to import other resources like Cloud Run service, service accounts if they existed before Terraform.

Run terraform plan: Verify that there are "No changes" after successful imports.

Bash

terraform plan
6.2. GitHub Actions Setup
GCP Authentication for GitHub Actions (Workload Identity Federation - Recommended):
The deploy.yml is configured to use Workload Identity Federation (WIF) with id-token: 'write'. This is the most secure method. Follow Google Cloud's documentation to set up an Identity Provider and grant the necessary IAM roles to a Service Account that your GitHub Actions workflow will assume. Remove any GCP_SA_KEY GitHub Secrets once WIF is fully configured and working.

Cloudflare API Credentials (GitHub Secrets):

Go to your GitHub repository > Settings > Secrets and variables > Actions > New repository secret.

Add:

CLOUDFLARE_API_TOKEN: Your Cloudflare API Token (Zone / Cache Purge permission only).

CLOUDFLARE_ZONE_ID: Your Cloudflare Zone ID for your domain.

Automatic Deployments:

Any git push to the main branch will automatically trigger the deploy.yml workflow.

The workflow will:

Run Python unit tests for the backend.

Authenticate securely to GCP.

Build a Docker image of your Flask API, tag it with the commit SHA, and push it to Google Container Registry.

Run terraform apply to deploy (or update) your Cloud Run service with the new image.

Synchronize your frontend files from the repository root to the GCS bucket.

Purge the Cloudflare CDN cache for your domain, ensuring new content is immediately visible.

7. Monitoring & Logging
Cloud Run Logging: View Cloud Run service logs directly in Cloud Logging for backend API activity.

Firestore Monitoring: Monitor database performance and usage in the Firestore Console.

Cloud Storage Monitoring: Track bucket activity and data transfer in the Cloud Storage Console.

Cloudflare Analytics: Cloudflare provides detailed analytics for your frontend traffic, caching, and security.

8. Security Considerations
Least Privilege: All service accounts and IAM roles are configured with the minimum necessary permissions.

Secrets Management: Sensitive values (like Cloudflare API keys) are stored as GitHub Secrets, not directly in code. GCP authentication uses Workload Identity Federation to avoid persistent keys in GitHub Actions.

HTTPS Only: Ensure Cloudflare is configured to enforce HTTPS for all traffic to your domain.

Uniform Bucket-Level Access: The GCS bucket is configured for uniform bucket-level access, simplifying permissions management.

9. Contributing
Feel free to fork this repository, adapt it for your own Cloud Resume Challenge, or suggest improvements!

10. License
This project is open-source and available under the MIT License.
