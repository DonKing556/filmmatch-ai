# FilmMatch AI

AI-powered movie recommendation engine — solo or with friends. Reduces decision fatigue and gets users to a confident "let's watch this" in under 90 seconds.

## Tech Stack

- **Backend:** Python 3.11 / FastAPI 0.115 / Uvicorn
- **Frontend:** Next.js 15 / React 19 / TypeScript / Tailwind 4 / Framer Motion
- **Database:** PostgreSQL 16 (asyncpg + SQLAlchemy 2.0 + Alembic)
- **Cache:** Redis 7 (redis-py)
- **AI:** Claude API (anthropic SDK 0.42) with model routing (Haiku 80% / Sonnet 18% / Opus 2%)
- **Movie Data:** TMDB API
- **Auth:** JWT + Magic Links (itsdangerous) + Google OAuth
- **Monitoring:** Sentry, Prometheus, PostHog, structlog
- **Deploy:** Railway (backend), Vercel (frontend), Resend (email)

## Architecture

**Hybrid AI pattern** — Claude never invents movies. TMDB provides verified candidates (30-50 real films), Claude ranks and reasons over them. This eliminates hallucination.

**Model routing** by complexity score:
- Haiku: simple solo requests (~80%, lowest cost)
- Sonnet: multi-user, refined requests (~18%)
- Opus: large groups, heavy constraints (~2%)

**Prompt caching** saves ~90% on system prompt tokens. **Pattern caching** targets 15-25% hit rate on common preference combos.

## Project Structure

```
backend/
  app/
    api/routes/       # auth, recommend, movies, groups, users, ops
    services/         # ai_service, tmdb_service, auth_service, taste_profile, email_service, sync_service
    core/             # config, deps, logging, metrics, redis, audit, sanitize, rate_limit
    db/               # models.py (9 models), session.py
    schemas/          # Pydantic request/response models
    prompts/          # Claude system prompt (filmmatch_system.md)
  tests/
    unit/             # 9 test files
    integration/      # test_api.py (full endpoint flows)
    quality/          # golden test cases
  alembic/            # Database migrations
frontend/
  src/
    app/              # Next.js App Router pages (/, /solo, /group, /group/join, /onboarding, /watchlist, /terms, /privacy)
    components/       # ui/, movie/, group/, layout/, feedback/
    hooks/            # useStreamRecommendation (SSE)
    stores/           # Zustand (preferences, ui)
    lib/              # api.ts, analytics.ts, helpers
    types/            # TypeScript types
  e2e/                # Playwright tests
```

## API

All routes mounted under `/api/v1/` prefix. Key endpoints:
- `POST /api/v1/auth/magic-link` + `POST /api/v1/auth/verify`
- `POST /api/v1/recommendations` + `/refine` + `/react` + `/select`
- `GET /api/v1/movies/trending` + `/{tmdb_id}` + `/{tmdb_id}/availability`
- `POST /api/v1/groups` + `/{code}/join` + `/{id}/recommend`
- `GET /api/v1/ops/readiness` + `/stats` + `/launch-check`
- `GET /metrics` (Prometheus)

## Development Commands

```bash
# Full stack (dev)
docker compose up

# Backend only
cd backend && uvicorn app.main:app --reload

# Frontend only
cd frontend && npm run dev

# Tests
cd backend && pytest tests/ -v
cd backend && pytest tests/ -v --cov=app
cd frontend && npx playwright test

# Linting & types
cd backend && ruff check .
cd backend && mypy app/
cd frontend && npm run lint
cd frontend && npm run type-check

# Database migrations
cd backend && alembic revision --autogenerate -m "description"
cd backend && alembic upgrade head
cd backend && alembic downgrade -1
```

## Conventions

- Backend uses async/await throughout (asyncpg, async SQLAlchemy)
- Pydantic Settings loads from `.env` file (`backend/.env`)
- Structured logging via structlog (`get_logger("module_name")`)
- Custom exceptions inherit from `FilmMatchError` (in `core/exceptions.py`)
- Frontend uses Zustand for client state, React Query for server state
- UI components use Radix primitives + Tailwind + Framer Motion
- Dark theme with violet/cyan design tokens and glass morphism

## Current Status

Version 0.3.0 — Feature-complete, preparing for launch. Working through deployment blockers (migrations, email, CI/CD, infra).
