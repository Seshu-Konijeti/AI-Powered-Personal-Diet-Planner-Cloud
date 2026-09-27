# System Architecture

## 1. Explanation

**Simple explanation:** The app is a website where you sign up, tell it a bit about yourself
(age, activity level, diet type, goal), and it generates a sample daily meal plan for you.
Your account, profile, and plans are saved centrally ("in the cloud") so you can log in from
any device and see the same data — instead of everything living only on one browser or phone.

**Technical explanation:** A React/HTML frontend calls a Flask REST API over HTTPS. The API
authenticates requests with JWTs, reads/writes structured data (users, plans, file metadata)
through a Cloud Database Service abstraction (SQLAlchemy → SQLite locally / managed Postgres
in the cloud), and stores raw uploaded files through a separate Cloud Object Storage Service
abstraction (local folder simulation → S3-compatible bucket in the cloud). An AI Engine module
generates the diet plan, either from a rule-based dataset or an external AI API, with automatic
fallback if the API is unavailable.

## 2. High-Level Data Flow

```
User
 ↓
Web Application (frontend/*.html)
 ↓
Authentication (JWT issued on /login)
 ↓
User Profile Input (profile.html → PUT /profile)
 ↓
Cloud Backend / REST API (backend/app.py + routes/*)
 ↓
AI Diet Planner (ai_engine/diet_engine.py)
 ↓
Personalized Plan
 ↓
Cloud Database (cloud/database_service.py → SQLite/Postgres)
 ↓
Cloud Storage (cloud/storage_service.py → local bucket/S3, for uploaded files)
 ↓
User Dashboard (dashboard.html)
```

## 3. Layered Architecture

```
CLIENT LAYER
  Web Browser
    ↓
  HTML/CSS/JS Frontend (frontend/)
    ↓
APPLICATION LAYER
  REST API
    ↓
  Python Flask (backend/app.py, backend/routes/*)
    ↓
AUTHENTICATION
  Flask-JWT-Extended (stateless JWT, bcrypt password hashing)
    ↓
        ┌─────────────┬──────────────┐
        ↓             ↓              ↓
   AI ENGINE      CLOUD DB      CLOUD STORAGE
 (ai_engine/)  (cloud/database  (cloud/storage_
                _service.py)     service.py)
        ↓             ↓              ↓
              Diet Plan / Files
                    ↓
              User Dashboard
```

## 4. Component Responsibilities

| Layer | Component | Responsibility |
|---|---|---|
| Client | `frontend/*.html`, `css/`, `js/api.js` | UI, calls REST API, stores JWT client-side |
| Application | `backend/app.py` | App factory, config, error handlers, route registration |
| Application | `backend/routes/*.py` | Request/response handling per resource (auth, profile, plans, files) |
| Application | `backend/utils/security.py` | Password hashing, input validation |
| AI | `ai_engine/diet_engine.py` | Rule-based generation + optional AI API + fallback logic |
| Data | `cloud/database_service.py` | All structured-data CRUD, user-scoped queries |
| Data | `backend/models/models.py` | ORM schema (Users, DietPlans, UserFiles) |
| Storage | `cloud/storage_service.py` | File save/delete, backend-swappable (local/S3) |

## 5. Why this shape

- **Separation of Database vs Object Storage** mirrors real cloud platforms (e.g. RDS vs S3):
  structured, queryable data goes in the database; binary blobs go in object storage.
- **Service-layer abstraction** (`cloud/*.py`) means swapping SQLite→Postgres or local→S3
  requires changing environment variables and one class, not every route.
- **Stateless JWT auth** means the API can be horizontally scaled (any instance can validate
  a token) — a prerequisite for cloud auto-scaling.
