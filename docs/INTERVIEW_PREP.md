# Interview Preparation

**1. Explain your project.**
It's an AI-powered personal diet planner that demonstrates cloud computing concepts end to
end. Users register and log in with JWT-based authentication, fill out a demo profile, and
generate a daily diet plan from a rule-based AI engine (with an optional external AI API and
automatic fallback). Plans are saved in a cloud database, and users can upload files to a
separate cloud object storage layer. I built it with Flask, SQLAlchemy, and a service-layer
abstraction so the same code can run locally on SQLite/local disk or point at managed cloud
services like Postgres and S3 just by changing environment variables.

**2. How does this project demonstrate cloud computing, not just a diet app?**
The core learning objective wasn't the nutrition logic — it was the architecture: separating
the database layer from the object storage layer, externalizing all configuration through
environment variables, designing stateless authentication so the API can scale horizontally,
and documenting both a free-tier and an AWS/Azure/GCP deployment path.

**3. What's the difference between your cloud database and cloud storage, and why keep them separate?**
The database (`cloud/database_service.py`) holds structured, queryable data — users, plans,
and file metadata. Object storage (`cloud/storage_service.py`) holds raw file bytes, addressed
by a key/path. Keeping them separate mirrors real systems like RDS + S3: it keeps the database
small and fast, and lets file storage scale independently and near-infinitely.

**4. How did you implement authentication and authorization?**
Passwords are hashed with bcrypt before being stored. On login, I issue a JWT with an 8-hour
expiry. Every protected route uses `@jwt_required()`, and — critically — every database query
is scoped by the `user_id` extracted from the JWT, not a value the client can send, so one
user can never fetch another user's plans or files even if they guess an ID.

**5. Walk me through your REST API design.**
I organized routes into blueprints by resource: `auth` (`/register`, `/login`, `/logout`),
`profile` (`GET`/`PUT /profile`), `plans` (`/generate-plan`, `/plans`, `/plans/{id}`), and
`files` (`/upload`, `/files`, `/files/{id}`). I used proper HTTP verbs and status codes — 201
for creation, 401 for auth failures, 404 for missing/forbidden resources, 409 for conflicts.

**6. How did you integrate AI, and what happens if the AI service fails?**
There are two versions: a rule-based engine that always works, and an optional external AI API
call. The API call is wrapped in a try/except with response validation; if the key isn't set,
the call fails, or the response doesn't parse into the expected JSON shape, the function
returns `None` and the caller transparently falls back to the rule-based engine — so the app's
core functionality never breaks due to an external dependency.

**7. How would this application scale to more users?**
Because auth is stateless (JWT), I could run multiple API instances behind a load balancer with
no session-affinity issues. The database would move from SQLite to a managed Postgres instance
(with read replicas at higher scale), the frontend would go behind a CDN, and heavier work like
AI generation could move to an async job queue or a serverless function.

**8. What security measures did you implement?**
Bcrypt password hashing, JWT-based auth with server-side revocation on logout, environment-
variable-based secrets (nothing hardcoded, `.env` git-ignored), input validation on registration
and file uploads (extension + size limits), CORS configuration, and strict per-user data scoping
to prevent one user from accessing another's data (an IDOR-style vulnerability I specifically tested for).

**9. How would you deploy this to the cloud?**
Two documented paths: a free-tier path using Render/Railway for the backend, their managed
Postgres add-on, Supabase/Firebase for storage, and Netlify/GitHub Pages for the static
frontend; and an AWS path using EC2 or Elastic Beanstalk, RDS, S3, and CloudFront, with secrets
in Secrets Manager. I also set up a GitHub Actions workflow that runs my test suite on every push.

**10. How did you test this, and what happens if the database goes down?**
I wrote 15 automated pytest tests covering registration, login, authorization, profile updates,
diet-plan generation across preferences/goals, AI-fallback behavior, plan/file persistence, and
— importantly — a test proving one user cannot retrieve another user's plan. For database
failures, Flask's error handlers catch unhandled exceptions and return a clean 500 JSON
response instead of leaking a stack trace or crashing the process.
