This project implements the Google Cloud Resume Challenge on GCP.
Static resume content is stored in a public GCS bucket and served behind Cloudflare (DNS + CDN + SSL).
The page loads JavaScript that calls a Cloud Run–hosted Flask API to increment and return a visitor count stored in Firestore.
All infrastructure (Cloud Run, IAM, APIs, etc.) is managed using Terraform, and CI/CD is automated through GitHub Actions and Cloud Build. 

- **Frontend:** Static resume hosted in **Google Cloud Storage (GCS)** and served via **Cloudflare** for DNS/CDN/SSL.  
- **Backend:** Python **Flask API** deployed on **Cloud Run** to handle visitor count logic.  
- **Database:** **Firestore** stores the visitor count in a native NoSQL database.  
- **Infrastructure as Code:** Managed via **Terraform**.  
- **CI/CD:** Automated with **GitHub Actions** and **Google Cloud Build** for container builds.  

---

flowchart TD
    subgraph UserSide["User Browser"]
      BHTML[Static Resume: HTML / CSS / JS]
    end

    subgraph CDN["Cloudflare (DNS/CDN/SSL)"]
    end

    subgraph GCS["GCS Bucket: www.temitayoapata.online"]
      Files[Static Assets: index.html, style.css, script.js]
    end

    subgraph API["Cloud Run Service: Flask Visitor Counter"]
      App[Containerized Flask App: count_visitors()]
    end

    subgraph DB["Firestore (Native)"]
      Doc[Document: views/counter {count:int}]
    end

    BHTML -- "Loads via HTTPS" --> CDN
    CDN -- "Origin fetch" --> GCS

    %% Browser JS calls API
    BHTML -- "JS fetch" --> API

    API --> DB
    DB --> API
    API --> BHTML

    %% Notes
    note over API,DB: "Cloud Run SA with roles/datastore.user"
    note over BHTML,API: "CORS allow origin www.temitayoapata.online"


CI/CD Workflow

flowchart LR
    GH[GitHub: Repo (main)] --> GA[GitHub Actions: deploy.yml]
    GA --> Tests[Run Pytest]
    Tests --> Build[Cloud Build: Build & Push Image]
    Build -->|gcr.io/project/service:SHA| AR[Artifact Registry]

    GA --> TF[Terraform Apply via GitHub Actions]
    TF --> CR[Cloud Run: Update Revision]
    TF --> FS[Enable Firestore API]
    TF --> SA[Create Service Account + IAM]
    TF --> GCSbkt[GCS Bucket Config]

    GA --> SyncGCS[gcloud storage rsync: Upload Frontend]
    SyncGCS --> GCSbkt

    Users[End Users] -->|DNS/HTTPS| CF[Cloudflare] --> GCSbkt
    Users -. "JS fetch" .-> CR
    CR --> Firestore[(Firestore DB)]


ASCII Fallback (For environments without Mermaid)
Architecture Overview:

 End User -> Cloudflare (DNS/CDN) -> GCS Bucket (Static HTML/CSS/JS)
            | JS Fetch |
            v
        Cloud Run (Flask API) -> Firestore (Visitor Count)
CI/CD Overview:


 GitHub -> GitHub Actions (Pytest -> Build Image -> Push to GCR)
            -> Terraform Apply (Update Cloud Run, Firestore, IAM)
            -> gcloud rsync (Upload Frontend to GCS)