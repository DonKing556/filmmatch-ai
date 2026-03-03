# FilmMatch AI — Deployment & Operations Guide

## Environments

| Environment | URL | Trigger |
|---|---|---|
| Development | localhost:8000 / localhost:3000 | `docker compose up` |
| Staging | staging.filmmatch.ai | Push to `main` |
| Production | filmmatch.ai | Git tag `v*` |

## Pre-Deployment Checklist

1. All CI checks pass (lint, type-check, tests)
2. No `change-me` secrets in production `.env`
3. Database migrations are up to date: `alembic upgrade head`
4. Run the launch readiness check: `GET /api/v1/ops/launch-check`

## Deployment

### Staging (automatic)

Every push to `main` triggers:
1. Backend + frontend tests
2. Docker image build and push to GHCR
3. Deploy to staging environment

### Production

```bash
# Tag a release
git tag v0.3.0
git push origin v0.3.0
```

This triggers the `release.yml` workflow which builds versioned Docker images and deploys to production.

### Manual Deploy (Docker Compose)

```bash
# Pull latest images
IMAGE_TAG=v0.3.0 docker compose -f docker-compose.prod.yml pull

# Deploy with zero-downtime
IMAGE_TAG=v0.3.0 docker compose -f docker-compose.prod.yml up -d

# Verify health
curl http://localhost:8000/api/v1/health

# Run smoke test
python backend/scripts/smoke_test.py --base-url http://localhost:8000

# Warm up caches
curl -X POST http://localhost:8000/api/v1/ops/warmup
```

## Post-Deployment Verification

1. **Smoke test**: `python backend/scripts/smoke_test.py`
2. **Launch check**: `GET /api/v1/ops/launch-check`
3. **Cache warmup**: `POST /api/v1/ops/warmup`
4. **Metrics**: Verify `/metrics` is serving Prometheus data
5. **Sentry**: Verify error tracking with a test error

## Rollback Procedure

### Quick Rollback (< 2 min)

```bash
# 1. Find the previous working tag
git tag --sort=-creatordate | head -5

# 2. Redeploy previous version
IMAGE_TAG=v0.2.0 docker compose -f docker-compose.prod.yml pull
IMAGE_TAG=v0.2.0 docker compose -f docker-compose.prod.yml up -d

# 3. Verify health
curl http://localhost:8000/api/v1/health
```

### Database Rollback

```bash
# Check current revision
alembic current

# Downgrade one step
alembic downgrade -1

# Or downgrade to specific revision
alembic downgrade <revision_id>
```

**Important**: Only roll back migrations if the new migration caused data issues. Most deployments are backwards-compatible and don't require migration rollback.

## Infrastructure

| Component | Provider | Notes |
|---|---|---|
| Backend | Railway | Docker container, auto-deploys from `backend/` |
| Database | Railway Postgres | Managed PostgreSQL 16, auto-backup |
| Cache | Railway Redis | Managed Redis 7, 128MB |
| Frontend | Vercel | Native Next.js 15, auto-deploys on push to main |
| Email | Resend | Magic link emails, 100/day free tier |
| Error Tracking | Sentry | Backend + Frontend, 10% trace sample |
| Analytics | PostHog | Product metrics, user flows |

## Monitoring

### Railway Dashboard
Railway provides built-in metrics for each service:
- CPU and memory usage
- Network I/O
- Deploy logs and health check status

### Prometheus Metrics
The backend exposes custom metrics at `GET /metrics`:
- `filmmatch_recommendations_total` — by mode, model, complexity tier
- `filmmatch_recommendation_latency_seconds` — histogram (P50/P95/P99)
- `filmmatch_claude_requests_total` — by model and status
- `filmmatch_tmdb_requests_total` — by endpoint and status
- `filmmatch_tmdb_cache_hits_total` / `misses_total`
- `filmmatch_rate_limit_hits_total` — by route

### Grafana Cloud (optional)
1. Create a free Grafana Cloud account
2. Add a Prometheus data source: `https://<railway-url>/metrics`
3. Create dashboards for recommendation latency, API costs, cache hit rates

## Post-Deploy Script

```bash
BACKEND_URL=https://your-backend.railway.app ./scripts/post-deploy.sh
```

This runs health check, cache warmup, movie sync, and launch readiness check.

## Monitoring Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /api/v1/health` | Basic health check (load balancer) |
| `GET /api/v1/ops/readiness` | Dependency checks (Kubernetes readiness) |
| `GET /api/v1/ops/stats` | Operational statistics |
| `GET /api/v1/ops/launch-check` | Comprehensive pre-launch report |
| `POST /api/v1/ops/warmup` | Populate caches with trending data |
| `POST /api/v1/ops/sync-movies` | Manually trigger TMDB catalog sync |
| `GET /metrics` | Prometheus metrics |

## Key Metrics to Monitor

- **P95 recommendation latency** — target < 5s
- **Error rate** — target < 1%
- **Claude API cost per recommendation** — target < $0.05
- **TMDB cache hit rate** — target > 50%
- **Rate limit rejections** — watch for spikes
- **Active sessions** — via `/ops/stats`

## Environment Variables

See `backend/.env.example` for all required variables. Critical for production:

- `ANTHROPIC_API_KEY` — Claude API access
- `TMDB_API_KEY` — Movie data
- `JWT_SECRET_KEY` — Auth token signing (use a strong random value)
- `MAGIC_LINK_SECRET` — Magic link signing
- `DATABASE_URL` — PostgreSQL connection string
- `REDIS_URL` — Redis connection string
- `SENTRY_DSN` — Error tracking (optional but recommended)
- `ENVIRONMENT=production` — Enables production behaviors

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| 502 on recommendations | TMDB API key invalid | Check `TMDB_API_KEY` |
| Slow first request | Cold cache | Run `POST /ops/warmup` |
| 429 errors | Rate limit hit | Check `/metrics` for `filmmatch_rate_limit_hits_total` |
| Redis connection errors | Redis down or wrong URL | Check `REDIS_URL`, verify Redis is running |
| "Internal server error" | Check Sentry | Look at Sentry dashboard for stack trace |
