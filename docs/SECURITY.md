# Cloud Security

## Concepts and where they're applied

- **Authentication** — `POST /login` verifies credentials and issues a JWT (`flask_jwt_extended`).
- **Authorization** — every protected route uses `@jwt_required()`; every database query is
  scoped by the authenticated `user_id` (never trusts a client-supplied user ID).
- **Password security** — passwords are hashed with bcrypt (`backend/utils/security.py`),
  salted automatically, never stored or logged in plaintext.
- **HTTPS** — not terminated by this demo app itself; the cloud platform (Render/Railway/
  CloudFront/ALB) terminates TLS in front of it. Always deploy behind HTTPS in production.
- **Encryption in transit** — guaranteed once deployed behind HTTPS (see above).
- **Encryption at rest** — managed cloud databases/buckets (RDS, S3, Cloud SQL) encrypt at
  rest by default; enable this option when provisioning them.
- **Environment variables** — all secrets (`JWT_SECRET_KEY`, `DATABASE_URL`, `AI_API_KEY`,
  AWS credentials) are read via `os.getenv(...)`, never hardcoded.
- **Secrets management** — `.env` is git-ignored (`.gitignore`); in the cloud, secrets live in
  the platform's environment variable store or a dedicated secrets manager.
- **API-key protection** — the optional AI API key is never sent to the frontend and never
  logged; it only exists server-side in `ai_engine/diet_engine.py`.
- **Database access rules** — the Cloud Database Service (`cloud/database_service.py`) is the
  only code path that touches the DB; every query filters by `user_id`.
- **Object-storage permissions** — files are stored under a per-user path
  (`storage_bucket/user_<id>/...`); in the S3 stub, this maps to per-user key prefixes, which
  in a real deployment would be paired with IAM bucket policies.
- **Input validation** — email format, password length, allowed file extensions, and file size
  limits are all validated server-side (`backend/utils/security.py`, `backend/routes/files.py`).
- **Rate limiting** — not implemented in this demo; recommended production addition is
  `Flask-Limiter` on `/login` and `/register` to slow brute-force attempts.
- **CORS** — configured via `CORS_ORIGIN` env var (`backend/app.py`); restrict this to your
  actual frontend domain in production instead of `*`.
- **Logging** — Flask's request logs plus recommended cloud-native logging (CloudWatch/Cloud
  Logging/Azure Monitor) once deployed — never log passwords, tokens, or full request bodies.
- **Backups** — managed cloud databases (RDS/Cloud SQL/Supabase) offer automated daily backups;
  enable this when provisioning your production database.

## Common mistakes students should avoid

1. Committing `.env` or real credentials to GitHub — always double-check `.gitignore`.
2. Storing passwords in plaintext or with a fast, unsalted hash (use bcrypt, not MD5/SHA1).
3. Trusting a `user_id` sent from the client instead of the one embedded in the JWT.
4. Leaving `CORS_ORIGIN=*` and `FLASK_DEBUG=true` in a production deployment.
5. Returning different error messages for "wrong password" vs "user not found" (enables
   account enumeration) — this project intentionally returns the same generic message.
6. Uploading files without validating extension/size, enabling storage abuse or malicious files.
7. Forgetting to revoke JWTs on logout, leaving tokens valid until natural expiry.
