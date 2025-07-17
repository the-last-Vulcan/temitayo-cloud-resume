This project implements the Google Cloud Resume Challenge on GCP.
Static resume content is stored in a public GCS bucket and served behind Cloudflare (DNS + CDN + SSL).
The page loads JavaScript that calls a Cloud Run–hosted Flask API to increment and return a visitor count stored in Firestore.
All infrastructure (Cloud Run, IAM, APIs, etc.) is managed using Terraform, and CI/CD is automated through GitHub Actions and Cloud Build.

flowchart TD
    subgraph UserSide["User Browser"]
      BHTML[Static Resume<br/>HTML/CSS/JS]
    end

    subgraph CDN["Cloudflare (DNS/CDN/SSL)"]
    end

    subgraph GCS["GCS Bucket<br/>www.temitayoapata.online"]
      Files[Static Assets<br/>index.html, style.css, script.js]
    end

    subgraph API["Cloud Run Service<br/>Flask Visitor Counter"]
      App[Containerized Flask App<br/>count_visitors()]
    end

    subgraph DB["Firestore (Native)"]
      Doc[views/counter<br/>{count:int}]
    end

    BHTML -- loads via HTTPS --> CDN
    CDN -- origin fetch --> GCS

    %% Browser JS calls API
    BHTML -- JS fetch --> API

    API --> DB
    DB --> API
    API --> BHTML

    %% Notes
    note over API,DB: Cloud Run SA w/ roles/datastore.user
    note over BHTML,API: CORS allow origin www.temitayoapata.online


flowchart LR
    GH[GitHub<br/>Repo (main)] --> GA[GitHub Actions<br/>deploy.yml]
    GA --> Tests[Run Pytest]
    Tests --> Build[Cloud Build<br/>Build & Push Image]
    Build -->|gcr.io/project/service:SHA| AR[Artifact Registry / GCR]

    GA --> TF[Terraform Apply<br/>via GitHub Actions]
    TF --> CR[Cloud Run<br/>Update Revision]
    TF --> FS[Firestore APIs Enabled]
    TF --> SA[Service Account + IAM]
    TF --> GCSbkt[GCS Bucket Config]

    GA --> SyncGCS[gcloud storage rsync<br/>Static Frontend Upload]
    SyncGCS --> GCSbkt

    Users[End Users] -->|DNS/HTTPS| CF[Cloudflare] --> GCSbkt
    Users -.JS fetch.-> CR
    CR --> Firestore[(Firestore)]
