# AI-Powered Personal Diet Planner with Cloud Storage
**Live demo:** https://ai-diet-planner-cloud.netlify.app (free-tier hosting: the first load can take about a minute while the backend wakes up)
> Educational Cloud Computing course project. Uses synthetic/demo data only. Generated diet
> plans are general wellness examples, **not medical or clinical nutrition advice**.

## Overview

A full-stack web application that generates personalized daily diet plans and demonstrates
core cloud computing concepts end-to-end: authentication, a cloud database, cloud object
storage, a REST API, an AI recommendation engine with fallback, and a documented cloud
deployment path — all runnable for free.

## Problem Statement

Most student diet-planner projects are single-file scripts with no persistence or auth. This
project instead uses the diet planner as a vehicle to build and document a real, cloud-shaped
architecture that runs entirely on free-tier/local tools.

## Objectives

- Working authentication with per-user data isolation
- Clean separation of a Cloud Database (structured data) and Cloud Object Storage (files)
- AI-generated diet plans with an always-available rule-based fallback
- A REST API following proper HTTP conventions
- A documented path from local simulation to real cloud deployment
- Automated tests + CI, and GitHub-ready proof-of-work documentation

## Features

- Register / Login / Logout (JWT-based sessions, bcrypt password hashing)
- Demo profile: age, height, weight, activity level, dietary preference, goal, allergies
- AI-generated plan: breakfast, lunch, snack, dinner, nutrition summary, hydration reminder
- Save / list / view / delete diet plans
- Upload / list / delete files to a simulated cloud object storage bucket
- Dashboard summarizing profile, latest plan, plan history, and files

## Cloud Computing Concepts

See [`docs/CLOUD_CONCEPTS.md`](docs/CLOUD_CONCEPTS.md) for a full table mapping every
concept (Cloud Computing, SaaS/PaaS/IaaS, Cloud Storage, Cloud Database, Authentication, REST
API, Client-Server Architecture, Serverless, Scalability, Availability, Elasticity, Load
Balancing, API Gateway, Environment Variables, Secrets Management, Cloud Security, Logging,
Monitoring, Deployment, CI/CD) to the exact file/line where it's demonstrated.

## Architecture

```
User → Frontend (HTML/CSS/JS) → Authentication (JWT) → REST API (Flask)
        → AI Diet Planner → Personalized Plan
        → Cloud Database (SQLite/Postgres)      [structured data]
        → Cloud Storage (local bucket/S3)        [files]
        → User Dashboard
```

Full layered diagram and component breakdown: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, vanilla JavaScript (fetch API) |
| Backend | Python 3, Flask, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-CORS |
| Database | SQLite (local) → Postgres (cloud, via `DATABASE_URL`) |
| Object Storage | Local filesystem simulation → AWS S3 (via `STORAGE_BACKEND=s3`) |
| AI Engine | Rule-based recommendation engine + optional external AI API with fallback |
| Auth | JWT (Flask-JWT-Extended) + bcrypt password hashing |
| Testing | pytest (15 tests) |
| CI/CD | GitHub Actions (`.github/workflows/tests.yml`) |

## AI Recommendation Engine

`ai_engine/diet_engine.py` implements two versions:
- **Version A (always available):** rule-based, selecting meals from `ai_engine/food_data.json`
  based on dietary preference, activity level, and goal.
- **Version B (optional):** if `AI_API_KEY` is set, calls an external AI API first.

**Fallback logic:** if the AI API is unavailable, unconfigured, or errors/returns malformed
JSON, the engine silently falls back to Version A — the app always produces a plan.

## Authentication

- `POST /register` hashes the password with bcrypt before storing it.
- `POST /login` verifies the password and issues a JWT (8-hour expiry).
- `POST /logout` revokes the token via an in-memory blocklist (JTI-based).
- Every protected route requires a valid, non-revoked JWT, and every query is scoped by the
  `user_id` from the token — one user cannot retrieve another user's data (tested in
  `tests/test_app.py::test_user_a_cannot_retrieve_user_b_data`).

## Database Design

| Table | Key fields |
|---|---|
| `users` | `user_id` (PK), `name`, `email` (unique), `password_hash`, `age`, `height_cm`, `weight_kg`, `activity_level`, `dietary_preference`, `goal`, `allergies`, `created_at` |
| `diet_plans` | `plan_id` (PK), `user_id` (FK → users), `breakfast`, `lunch`, `snack`, `dinner`, `nutrition_summary`, `hydration_reminder`, `source`, `created_at` |
| `user_files` | `file_id` (PK), `user_id` (FK → users), `filename`, `storage_path`, `content_type`, `size_bytes`, `uploaded_at` |

## Cloud Storage

`cloud/storage_service.py` stores uploaded files under
`storage_bucket/user_<id>/<uuid>_<filename>` and keeps only metadata (filename, path, type,
size) in the database — exactly like pairing S3 with RDS/Postgres in production. Swap
`STORAGE_BACKEND=s3` (plus AWS credentials as env vars) to use a real bucket without touching
route code.

## REST API

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/register` | No | Create a new account |
| POST | `/login` | No | Authenticate, returns a JWT |
| POST | `/logout` | Yes | Revoke the current token |
| GET | `/profile` | Yes | Get the current user's profile |
| PUT | `/profile` | Yes | Update the current user's profile |
| POST | `/generate-plan` | Yes | Generate (and save) a diet plan |
| GET | `/plans` | Yes | List the current user's saved plans |
| GET | `/plans/{id}` | Yes | Get one plan (must belong to the user) |
| DELETE | `/plans/{id}` | Yes | Delete one plan |
| POST | `/upload` | Yes | Upload a file to cloud storage |
| GET | `/files` | Yes | List the current user's files |
| DELETE | `/files/{id}` | Yes | Delete a file |
| GET | `/health` | No | Health check (for uptime monitoring) |

## Folder Structure

```
AI-Personal-Diet-Planner-Cloud/
├── frontend/                # Static HTML/CSS/JS client
│   ├── css/style.css
│   ├── js/api.js             # Shared fetch wrapper + auth/token helpers
│   ├── index.html            # Landing page
│   ├── register.html / login.html
│   ├── profile.html          # Demo profile form
│   ├── generate.html         # Generate a plan
│   ├── result.html           # View a single generated plan
│   ├── saved_plans.html      # List/delete saved plans
│   ├── files.html            # Upload/list/delete cloud files
│   └── dashboard.html        # Aggregated overview
│
├── backend/
│   ├── app.py                 # App factory, config, error handlers
│   ├── routes/                # auth.py, profile.py, plans.py, files.py
│   ├── models/models.py       # SQLAlchemy models (Users, DietPlans, UserFiles)
│   └── utils/security.py      # Password hashing, validation helpers
│
├── ai_engine/
│   ├── diet_engine.py         # Rule-based + optional AI-API engine, with fallback
│   └── food_data.json         # Meal dataset used by the rule-based engine
│
├── cloud/
│   ├── database_service.py    # Cloud Database Service abstraction (all DB CRUD)
│   └── storage_service.py     # Cloud Object Storage abstraction (local/S3)
│
├── tests/test_app.py          # 15 automated pytest tests
├── .github/workflows/tests.yml# CI: runs pytest on every push
├── screenshots/                # Proof-of-work screenshots (see docs/SCREENSHOT_CHECKLIST.md)
├── sample_data/demo_users.json # Synthetic demo users for manual testing
├── docs/                       # Architecture, cloud concepts, deployment, security,
│                                # scalability, testing, GitHub strategy, report, interview prep
├── requirements.txt
├── .env.example
└── .gitignore
```

## Installation & Local Setup

```bash
git clone <your-repo-url> AI-Personal-Diet-Planner-Cloud
cd AI-Personal-Diet-Planner-Cloud
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## Environment Variables

See [`.env.example`](.env.example) — `DATABASE_URL`, `JWT_SECRET_KEY`, `CORS_ORIGIN`,
`STORAGE_BACKEND` (+ `S3_BUCKET_NAME` if using S3), `AI_API_PROVIDER` / `AI_API_KEY`
(optional), `FLASK_DEBUG`, `PORT`. Never commit a real `.env` file.

## Running the Application

```bash
# Terminal 1 — backend (http://localhost:5000)
python backend/app.py

# Terminal 2 — frontend (http://localhost:8000)
cd frontend && python3 -m http.server 8000
```
Open `http://localhost:8000/index.html`, register a demo user, and go.

Full 15-step local simulation walkthrough: [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

## Cloud Deployment

Two full deployment paths (free-tier PaaS, and AWS/Azure/GCP) with a local-vs-cloud comparison
table and a GitHub Actions CI workflow: [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

## Testing

```bash
pytest tests/ -v
```
15/15 automated tests passing, covering auth, authorization, profile updates, diet-plan
generation across preferences/goals, AI-fallback, plan/file persistence, cross-user data
isolation, and logout/token revocation. Full test-case table: [`docs/TESTING.md`](docs/TESTING.md).

## Security

Password hashing (bcrypt), stateless JWT auth with logout revocation, environment-variable
secrets, per-user data isolation, input/file validation, CORS configuration, and a list of
common student mistakes to avoid: [`docs/SECURITY.md`](docs/SECURITY.md).

## Scalability

How this architecture behaves and evolves at 10 / 1,000 / 100,000 users — auto-scaling, load
balancing, managed databases, CDN, caching, queues, serverless: [`docs/SCALABILITY.md`](docs/SCALABILITY.md).

## Screenshots

See [`docs/SCREENSHOT_CHECKLIST.md`](docs/SCREENSHOT_CHECKLIST.md) for the full list of
proof-of-work screenshots to capture and their filenames; save them into `screenshots/`.

## Results

The application runs end-to-end locally: authentication, profile management, AI-generated diet
plans (with verified rule-based fallback), plan persistence/retrieval, file upload to simulated
cloud storage, and a dashboard — all covered by a passing automated test suite.

## Limitations

Uses SQLite and local-disk storage by default (by design, to stay free); the optional AI-API
path is not exercised against a live paid API in this repo; not a medical/clinical tool.

## Future Improvements

Live managed Postgres + S3 deployment, production AI API integration, rate limiting, Redis-
backed JWT blocklist for true multi-instance scaling, and CD-driven automatic deployment.

## Learning Outcomes

Cloud database vs. object storage design, stateless authentication for scalability, REST API
design, environment-variable-based secrets management, automated testing, CI pipelines, and a
concrete free-tier-to-cloud deployment path.

## Disclaimer

This project uses only synthetic/demo data. Generated diet plans are educational/general
wellness examples and must not be treated as medical or clinical nutrition advice.

## Author

Rsk (Seshu) — student project for a Cloud Computing course.

## Related Documentation

[Architecture](docs/ARCHITECTURE.md) · [Cloud Concepts](docs/CLOUD_CONCEPTS.md) ·
[Deployment](docs/DEPLOYMENT.md) · [Testing](docs/TESTING.md) · [Security](docs/SECURITY.md) ·
[Scalability](docs/SCALABILITY.md) · [GitHub Strategy](docs/GITHUB_STRATEGY.md) ·
[Screenshot Checklist](docs/SCREENSHOT_CHECKLIST.md) · [Project Report](docs/PROJECT_REPORT.md) ·
[Resume/LinkedIn](docs/RESUME_LINKEDIN.md) · [Interview Prep](docs/INTERVIEW_PREP.md)
