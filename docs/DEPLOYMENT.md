# Local Simulation & Cloud Deployment

## Part 1 — Local / Virtual Simulation

Run everything on your own machine first, exactly the way it will run in the cloud.

```bash
# Step 1: Install Python 3.10+ and Git (one-time)

# Step 2: Get the project
git clone <your-repo-url> AI-Personal-Diet-Planner-Cloud
cd AI-Personal-Diet-Planner-Cloud

# Step 3: Create a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Step 4: Install dependencies
pip install -r requirements.txt

# Step 5: Configure environment variables
cp .env.example .env            # edit values if needed (defaults work out of the box)

# Step 6: Start the backend (http://localhost:5000)
python backend/app.py

# Step 7: Start the frontend (new terminal, http://localhost:8000)
cd frontend
python3 -m http.server 8000

# Step 8: Register a demo user
# Open http://localhost:8000/register.html in your browser

# Step 9: Complete your profile
# http://localhost:8000/profile.html

# Step 10: Generate a diet plan
# http://localhost:8000/generate.html

# Step 11: Save plan -> happens automatically on generation

# Step 12: Upload a sample file
# http://localhost:8000/files.html

# Step 13: Retrieve a previous plan
# http://localhost:8000/saved_plans.html

# Step 14: Test logout/login
# Click "Logout", then log back in with the same credentials

# Step 15: Verify stored data
sqlite3 diet_planner.db "SELECT user_id, name, email FROM users;"
ls storage_bucket/
```

## Part 2 — Cloud Deployment

### Approach A: Free-tier / Student-friendly (Render or Railway)

1. Push this repo to GitHub.
2. **Backend**: Create a new Web Service on Render/Railway, connect the GitHub repo, set:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn -w 2 -b 0.0.0.0:$PORT backend.app:app` (add `gunicorn` to requirements.txt for production)
   - Environment variables: copy every key from `.env.example`, generate a strong `JWT_SECRET_KEY`
3. **Database**: use the platform's free managed Postgres add-on; set `DATABASE_URL` to the
   connection string it gives you (`postgresql://...`). Add `psycopg2-binary` to requirements.txt.
4. **Object Storage**: for a true free-tier cloud bucket, create a free Supabase or Firebase
   Storage project and set `STORAGE_BACKEND` accordingly (extend `cloud/storage_service.py`
   with a `SupabaseStorageBackend`, following the `S3StorageBackend` stub pattern).
5. **Frontend**: deploy the static `frontend/` folder to GitHub Pages, Netlify, or Vercel (free).
   Set `window.API_BASE_OVERRIDE` in a small inline `<script>` on each page (or a shared
   `config.js`) to your deployed backend URL.
6. **Logs/Monitoring**: Render/Railway provide a built-in log stream and uptime dashboard —
   point it at `GET /health`.

### Approach B: AWS / Azure / GCP (advanced)

| Concern | AWS example | Azure example | GCP example |
|---|---|---|---|
| Frontend hosting | S3 static website + CloudFront (CDN) | Azure Static Web Apps | Cloud Storage static hosting |
| Backend hosting | Elastic Beanstalk / EC2 / Lambda + API Gateway | App Service | Cloud Run |
| Managed database | RDS (Postgres) | Azure Database for PostgreSQL | Cloud SQL |
| Object storage | S3 bucket | Blob Storage | Cloud Storage bucket |
| Auth | Cognito (or keep this project's JWT auth) | Azure AD B2C | Firebase Auth |
| Secrets | Secrets Manager / SSM Parameter Store | Key Vault | Secret Manager |
| Env vars | Elastic Beanstalk environment properties | App Service Configuration | Cloud Run environment variables |
| Logs | CloudWatch Logs | Azure Monitor | Cloud Logging |
| Monitoring | CloudWatch Alarms | Azure Monitor Alerts | Cloud Monitoring |

Steps (AWS EC2/RDS/S3 sketch):
1. Launch an EC2 instance (t2.micro, free tier) → install Python, clone repo, run with gunicorn behind Nginx.
2. Create an RDS Postgres instance (free tier) → set `DATABASE_URL`.
3. Create an S3 bucket → set `STORAGE_BACKEND=s3`, `S3_BUCKET_NAME`, and configure an IAM role
   with least-privilege S3 permissions for the EC2 instance (never hardcode AWS keys).
4. Put CloudFront in front of the S3-hosted frontend for CDN caching.
5. Store `JWT_SECRET_KEY`/DB creds in AWS Secrets Manager, injected as env vars at boot.

## Local Development vs Cloud Deployment

| Aspect | Local | Cloud |
|---|---|---|
| Database | SQLite file on disk | Managed Postgres (RDS/Cloud SQL/Supabase) |
| File storage | `storage_bucket/` folder | S3/Blob/Cloud Storage bucket |
| Secrets | `.env` file (git-ignored) | Platform env vars / Secrets Manager |
| Scaling | Single process | Multiple instances behind a load balancer |
| Access | `localhost` only | Public HTTPS URL |
| Monitoring | Terminal logs | Centralized logs + dashboards + alerts |

## CI/CD (recommended)

Add `.github/workflows/tests.yml` to run the test suite on every push:

```yaml
name: Run Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v
```
