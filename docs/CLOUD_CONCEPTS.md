# Cloud Computing Concepts Demonstrated

For every concept: what it means, and exactly where it appears in this project.

| Concept | Meaning | Where in this project |
|---|---|---|
| **Cloud Computing** | Delivering compute/storage/services over a network instead of a single local machine | The Flask API + database + storage are designed to run on remote infrastructure (Render/Railway/AWS), accessed by the frontend over HTTPS |
| **SaaS** (Software as a Service) | End users consume a ready-made application via the browser | The deployed diet-planner web app itself — a user just opens the URL and uses it |
| **PaaS** (Platform as a Service) | You deploy code; the platform manages OS/runtime/scaling | Deploying `backend/` to Render/Railway/Heroku — you provide `requirements.txt` + `app.py`, the platform runs it |
| **IaaS** (Infrastructure as a Service) | You manage VMs/networking yourself | The AWS EC2/Azure VM deployment option in `DEPLOYMENT.md` (Approach B) |
| **Cloud Database** | Managed, centrally hosted structured data store | `cloud/database_service.py` + `DATABASE_URL` — SQLite locally, swappable to AWS RDS / Cloud SQL / Supabase Postgres |
| **Cloud Storage / Object Storage** | Storing files/blobs by key, separate from structured data | `cloud/storage_service.py` — local bucket simulation, swappable to AWS S3 (`S3StorageBackend` stub) |
| **Authentication** | Verifying who a user is | `POST /login` issuing a JWT; `POST /register` with bcrypt-hashed passwords |
| **Authorization** | Verifying what an authenticated user may access | `@jwt_required()` + every query scoped by `user_id` (`get_plan_by_id_for_user`, etc.) |
| **REST API** | Stateless, resource-oriented HTTP API | `backend/routes/*.py` — `/register`, `/login`, `/profile`, `/plans`, `/files`, using proper HTTP verbs & status codes |
| **Client-Server Architecture** | Frontend and backend as separate, independently deployable tiers | `frontend/` (static HTML/JS) calling `backend/` (Flask API) over HTTP, communicating only via JSON |
| **Serverless Computing** | Running code without managing servers, billed per invocation | Discussed in `DEPLOYMENT.md`/`SCALABILITY.md` as an evolution path — e.g. moving `/generate-plan` to AWS Lambda behind API Gateway |
| **Scalability** | Ability to handle more load by adding resources | Stateless JWT auth + externalized DB/storage means you can run multiple API instances behind a load balancer — see `SCALABILITY.md` |
| **Availability** | The system stays up and reachable | Managed cloud DB/storage + health-check endpoint `GET /health` used by platform uptime monitors |
| **Elasticity** | Automatically scaling resources up/down with demand | Discussed in `SCALABILITY.md` — e.g. Render/AWS auto-scaling groups reacting to CPU/request metrics |
| **Load Balancing** | Distributing traffic across multiple server instances | Described in `SCALABILITY.md`; most PaaS providers add this automatically once you run >1 instance |
| **API Gateway** | Single entry point that routes, authenticates, and throttles API traffic | Discussed in `DEPLOYMENT.md` (Approach B) as the entry point in front of Lambda/EC2 |
| **Environment Variables** | Externalized configuration, no hardcoded secrets | `.env.example`, `os.getenv(...)` throughout `backend/app.py`, `cloud/storage_service.py`, `ai_engine/diet_engine.py` |
| **Secrets Management** | Keeping credentials out of source code/version control | `.env` is git-ignored; `JWT_SECRET_KEY`/`AI_API_KEY`/DB credentials are never hardcoded |
| **Cloud Security** | Protecting data/access in a shared, networked environment | Password hashing, JWT expiry, CORS config, per-user data isolation, input validation — see `SECURITY.md` |
| **Logging** | Recording application events for debugging/audit | Flask's built-in request logs; extension points noted in `SECURITY.md`/`DEPLOYMENT.md` for cloud logging (CloudWatch, etc.) |
| **Monitoring** | Observing system health over time | `GET /health` endpoint; platform dashboards (Render/Railway/CloudWatch) — see `DEPLOYMENT.md` |
| **Deployment** | Making the application reachable in the cloud | `DEPLOYMENT.md` — free-tier approach (Approach A) and AWS/Azure/GCP approach (Approach B) |
| **CI/CD** | Automated build/test/deploy pipeline | Recommended GitHub Actions workflow (run `pytest` on every push) described in `DEPLOYMENT.md` |
