# Project Report: AI-Powered Personal Diet Planner with Cloud Storage

## Abstract
This project implements a full-stack, cloud-oriented web application that generates
personalized, general-wellness diet plans using a rule-based AI engine (with an optional
external AI API and automatic fallback), while demonstrating core cloud computing concepts:
authentication, a cloud database, cloud object storage, a REST API, and cloud deployment.

## Introduction
Personal nutrition tools are widely used, but most course projects stop at a simple local
script. This project instead treats the diet planner as a vehicle for demonstrating cloud
architecture end-to-end — from client to API to AI engine to database and object storage —
using entirely free-tier or local/simulated alternatives so it remains fully executable
without any paid service.

## Problem Statement
Students need a way to demonstrate practical cloud computing skills (auth, cloud DB, cloud
storage, REST APIs, deployment, security, scaling) through a project that is functional,
explainable, and free to run — rather than a purely theoretical assignment.

## Objectives
- Build a working full-stack application with real authentication and data isolation.
- Demonstrate a clean separation between the Cloud Database (structured data) and Cloud
  Object Storage (files) layers.
- Implement an AI recommendation engine with a safe, always-available fallback path.
- Provide a clear path from local simulation to real cloud deployment.
- Produce GitHub-ready documentation, tests, and proof-of-work artifacts.

## Existing System
Most beginner diet-planner projects are single-file scripts with no persistence, no
authentication, and no distinction between structured data and file storage — they do not
demonstrate cloud concepts at all.

## Proposed System
A three-tier application: a static HTML/CSS/JS frontend, a Flask REST API backend, and two
cloud-service abstractions (`cloud/database_service.py`, `cloud/storage_service.py`) that can
point at local resources today and managed cloud resources (Postgres, S3, etc.) tomorrow with
only configuration changes.

## Cloud Computing Concepts
See `docs/CLOUD_CONCEPTS.md` for the full concept-by-concept mapping (Cloud Computing, SaaS,
PaaS, IaaS, Cloud Storage, Cloud Database, Authentication, REST API, Client-Server, Serverless,
Scalability, Availability, Elasticity, Load Balancing, API Gateway, Environment Variables,
Secrets Management, Cloud Security, Logging, Monitoring, Deployment, CI/CD).

## Technology Stack
Frontend: HTML5, CSS3, vanilla JavaScript (fetch API). Backend: Python, Flask, Flask-SQLAlchemy,
Flask-JWT-Extended, Flask-CORS, bcrypt. Database: SQLite locally / Postgres in the cloud. Object
Storage: local filesystem simulation / AWS S3 in the cloud. AI: custom rule-based engine with
optional external AI API integration and automatic fallback.

## System Architecture
See `docs/ARCHITECTURE.md` for the full layered diagram and data-flow description.

## Data Flow
User → Frontend → Authentication (JWT) → REST API → AI Engine → Cloud Database (plan saved) →
Cloud Storage (files saved) → Dashboard (aggregated view).

## Database Design
Three tables: `users`, `diet_plans` (FK → `users.user_id`), `user_files` (FK → `users.user_id`).
Every query for plans/files is scoped by the authenticated user's ID, enforcing per-user data
isolation at the query layer, not just the UI layer.

## Cloud Storage Design
Files are stored under `storage_bucket/user_<id>/<uuid>_<filename>`, with only lightweight
metadata (filename, path, type, size) kept in the database — mirroring how S3 + RDS/Postgres
work together in production systems.

## AI Recommendation Logic
`ai_engine/diet_engine.py` selects meals from `food_data.json` based on dietary preference,
activity level, and goal (Version A, always available). If `AI_API_KEY` is configured, an
external AI API is tried first (Version B); any failure — missing key, network error, malformed
response — silently falls back to Version A so the app never breaks.

## Authentication
Registration hashes passwords with bcrypt; login issues a JWT (8-hour expiry); logout adds the
token's JTI to a blocklist. All protected routes require a valid, non-revoked token.

## API Design
See `README.md` for the full endpoint table (`/register`, `/login`, `/logout`, `/profile`,
`/generate-plan`, `/plans`, `/plans/{id}`, `/upload`, `/files`, `/files/{id}`).

## Implementation
Full source code is organized into `frontend/`, `backend/`, `ai_engine/`, and `cloud/` — see
`README.md` → Folder Structure for a complete breakdown of every file's purpose.

## Testing
15 automated pytest tests cover registration, login, authorization, profile updates, diet-plan
generation (all preferences/goals), AI-fallback behavior, plan persistence, file upload/
validation, cross-user data isolation, and logout/token revocation. See `docs/TESTING.md`.

## Cloud Deployment
Two deployment paths documented in `docs/DEPLOYMENT.md`: a free-tier path (Render/Railway +
managed Postgres + Supabase/Firebase storage) and an AWS/Azure/GCP path (EC2/RDS/S3 or
equivalents), plus a GitHub Actions CI workflow that runs the test suite on every push.

## Security
Password hashing, stateless JWT auth with revocation, environment-variable-based secrets,
per-user data isolation, input/file validation, and CORS configuration. Full detail in
`docs/SECURITY.md`.

## Scalability
Discussed at 10 / 1,000 / 100,000 user scales, covering managed databases, load balancing,
auto-scaling, CDN, caching, and serverless options. Full detail in `docs/SCALABILITY.md`.

## Results
The application runs locally end-to-end: registration, login, profile management, AI-generated
diet plans (rule-based, with fallback verified), plan persistence and retrieval, file upload to
simulated cloud storage, and a dashboard aggregating all of the above — all covered by a passing
automated test suite.

## Advantages
Fully free to run and demonstrate; clean separation of concerns; realistic cloud-service
abstractions that map directly onto real managed services; strong GitHub portfolio artifact.

## Limitations
Uses SQLite and local-disk storage by default rather than live managed cloud services (by
design, to stay free); the AI engine's "Version B" AI API path is optional and untested against
a live paid API in this repository; not intended for real medical/nutritional use.

## Future Scope
Add a real managed Postgres + S3 deployment, integrate a production AI API, add rate limiting,
introduce Redis-backed JWT blocklisting for true multi-instance scaling, and add CI/CD-driven
automatic deployment.

## Conclusion
This project demonstrates that a student, using only free-tier and local tools, can build and
document a genuinely cloud-architected application — covering authentication, cloud database
design, cloud object storage, REST APIs, AI integration with fallback, testing, security, and a
documented deployment path — suitable as strong, explainable proof of work.
