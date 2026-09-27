# Scalability

## What happens at different scales

**10 users** — The current architecture handles this trivially. A single Flask process, SQLite
or a small managed Postgres instance, and local/small S3 storage are more than enough. No
changes needed.

**1,000 users** — SQLite becomes a bottleneck (file-level locking, no concurrent writers at
scale) — move to a managed Postgres/MySQL instance (RDS/Cloud SQL). Run the Flask app behind
a WSGI server (gunicorn) with multiple worker processes. Because JWT auth is stateless, you can
run 2-3 backend instances behind a simple load balancer without any session-affinity concerns.
Add basic caching (e.g. cache the static `food_data.json` lookups in memory, already effectively
free) and monitor response times.

**100,000 users** — Horizontal scaling becomes essential:
- **Auto-scaling groups**: run the API on multiple containers/VMs that scale out based on CPU/
  request-rate metrics (AWS ECS/EKS + Auto Scaling, or a PaaS's built-in autoscaler).
- **Load balancer**: distribute traffic across instances (ALB, Nginx, or the PaaS default).
- **Managed database with read replicas**: offload read-heavy endpoints (`GET /plans`,
  `GET /files`) to replicas; keep writes on the primary.
- **CDN**: serve the static frontend (HTML/CSS/JS) via CloudFront/Cloudflare so it's cached at
  edge locations close to users worldwide, instead of hitting the origin every time.
- **Object storage stays flat**: S3-style storage scales near-infinitely without extra work —
  this is one reason to keep files out of the database from day one (which this project already does).
- **Caching layer**: introduce Redis for hot data (e.g. rate-limit counters, JWT blocklist
  instead of the current in-memory set, which would not work correctly across multiple instances).
- **Queues**: if AI-generation calls become slow/expensive, move `/generate-plan` to an async
  job (SQS/Pub-Sub + a worker) and let the client poll or receive a webhook/notification instead
  of blocking the HTTP request.
- **Serverless functions**: stateless endpoints like `/generate-plan` are good Lambda/Cloud
  Functions candidates — you pay only per invocation and it scales to zero when idle.

## Why the current design scales well from the start

- **Stateless authentication** (JWT) — any instance can validate any request; no server-side
  session store required for basic scaling.
- **Cloud Database Service abstraction** — swapping SQLite for a managed, replicable database
  requires changing `DATABASE_URL` only.
- **Cloud Storage Service abstraction** — object storage backends (S3, etc.) already scale
  horizontally by design; this project's abstraction makes swapping to one a one-class change.
- **Clear separation of layers** (client / API / AI / data / storage) means each layer can be
  scaled or replaced independently as load grows.

## Interview-ready one-liner

> "The app is stateless at the API layer, so scaling starts with just running more instances
> behind a load balancer; the database and storage layers are already abstracted so they can be
> swapped for managed, horizontally-scalable cloud services without touching route code."
