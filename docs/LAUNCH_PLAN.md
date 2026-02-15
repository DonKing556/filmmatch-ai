# FilmMatch AI — Phased Launch Plan

**From Prototype to Production | Netflix-Level UI**
**Created: February 15, 2026**

---

## Executive Summary

FilmMatch AI is currently at **~11% production readiness** — a functional proof-of-concept with a well-written system prompt and clean architecture skeleton, but missing virtually everything needed for launch. This plan covers 6 phases over ~16 weeks to reach a launch-ready product.

### Current State Assessment

| Component | Readiness | What Exists | What's Missing |
|-----------|-----------|-------------|----------------|
| Backend API | 20% | 1 endpoint, Claude integration | Auth, DB, caching, rate limiting, error handling, logging |
| Frontend | 5% | Vite + React scaffold | Zero UI components, no pages, no state management |
| Database | 0% | Nothing | Entire persistence layer |
| AI Engine | 15% | System prompt + raw Claude call | TMDB integration, hallucination prevention, session management |
| Auth | 0% | Nothing | Entire auth system |
| Testing | 10% | 3 trivial tests | Real coverage, integration tests, E2E |
| DevOps | 30% | Docker + CI | Secrets, monitoring, CD, staging environment |
| Security | 10% | .gitignore for .env | Rate limiting, input validation, audit logging |

### Critical Architectural Pivot Required

**The current pure-LLM approach is fundamentally flawed.** Claude will hallucinate non-existent movies, has no current streaming data, and can't verify its own recommendations. The plan adopts a **hybrid architecture**: TMDB provides verified movie data → Claude ranks and reasons over that data.

---

## Phase 0: Foundation & Architecture Reset (Weeks 1-2)

**Goal:** Rebuild the backend foundation with the hybrid AI architecture, database, and core infrastructure.

### 0.1 — Hybrid AI Architecture

Replace the current "ask Claude to invent recommendations" approach with the candidate-set pattern:

```
User Preferences → TMDB API (fetch 30-50 real candidates) → Claude (rank & reason) → Validated Response
```

- Integrate TMDB API for movie search, discover, trending, and metadata
- Integrate Watchmode or JustWatch API for streaming availability
- Build candidate-selection pipeline: query TMDB based on genres/mood/era, return real movies with full metadata
- Claude's new role: rank candidates, match to mood, generate rationale — NOT generate movie titles from memory
- Add response validation: every recommendation must carry a valid `tmdb_id`; reject any hallucinated entries

### 0.2 — Database Layer (PostgreSQL)

Core tables:
- `users` — id, email, display_name, auth_provider, timestamps
- `user_preferences` — genres, actors, directors, streaming services, content rating
- `movies` — TMDB cache: title, overview, genres, ratings, cast, runtime, poster/backdrop paths
- `streaming_availability` — tmdb_id, service, region, link (refreshed weekly)
- `watch_history` — user_id, tmdb_id, status (watched/watchlist/dismissed), rating
- `recommendation_sessions` — preferences, recommendations, turns, model used, tokens
- `groups` + `group_members` — for group mode
- `analytics_events` — partitioned event log

Add Alembic for migrations. Set up nightly TMDB sync job.

### 0.3 — Redis

- Active session state (TTL: 30 min)
- Rate limit counters
- Recommendation pattern cache (TTL: 6 hours)
- TMDB trending/now-playing cache (TTL: 1 hour)

### 0.4 — Authentication

- Magic link (primary, lowest friction)
- Google OAuth (secondary)
- JWT: 15-min access tokens, 30-day refresh tokens
- Endpoints: `/auth/magic-link`, `/auth/verify`, `/auth/oauth/google`, `/auth/refresh`, `/auth/logout`

### 0.5 — Core API Expansion

```
POST   /api/v1/auth/magic-link
POST   /api/v1/auth/verify
POST   /api/v1/auth/oauth/google
GET    /api/v1/users/me
PATCH  /api/v1/users/me/preferences
POST   /api/v1/recommendations
GET    /api/v1/recommendations/stream          (SSE)
POST   /api/v1/recommendations/{id}/refine
POST   /api/v1/recommendations/{id}/react
POST   /api/v1/recommendations/{id}/select
GET    /api/v1/movies/trending
GET    /api/v1/movies/{tmdb_id}
GET    /api/v1/movies/{tmdb_id}/availability
GET    /api/v1/health
```

### 0.6 — Infrastructure

- Structured logging (structlog or loguru)
- Rate limiting middleware (per-user, per-IP)
- Error handling: proper exception classes, no stack trace leakage
- CORS configuration for production domains
- Environment-based config (dev/staging/prod)

### Deliverables
- [ ] TMDB API integration with candidate-set pipeline
- [ ] PostgreSQL schema + Alembic migrations
- [ ] Redis setup for sessions + caching
- [ ] Auth system (magic link + Google OAuth + JWT)
- [ ] Expanded API endpoints
- [ ] Rate limiting + structured logging + error handling
- [ ] Nightly TMDB sync job

---

## Phase 1: Design System & Core Frontend (Weeks 3-5)

**Goal:** Build the Netflix-caliber design system and core UI infrastructure.

### 1.1 — Tech Stack Setup

| Library | Purpose |
|---------|---------|
| **Next.js 14+ (App Router)** | SSR, image optimization, routing |
| **Tailwind CSS 4** | Zero-runtime styling, design token system |
| **Framer Motion 11+** | Layout animations, gestures, springs |
| **Radix UI** | Accessible unstyled component primitives |
| **Embla Carousel** | Netflix-style horizontal scroll rows |
| **TanStack React Query** | Server state, caching, background refetch |
| **Zustand** | Client state (preferences, UI state) |
| **Sonner** | Toast notifications |

### 1.2 — Design Tokens

**Color palette (cinematic dark theme):**
```
Backgrounds:  #0A0A0F → #12121A → #1A1A25 → #22222F
Accent:       #8B5CF6 (violet primary) → #06B6D4 (cyan secondary)
Gradient:     linear-gradient(135deg, #8B5CF6, #06B6D4)
Text:         rgba(255,255,255, 0.95/0.65/0.40)
Glassmorphism: rgba(255,255,255, 0.05) + blur(20px) + 1px border at 0.10
Success:      #22C55E  |  Warning: #EAB308  |  Error: #EF4444
```

**Typography:** Inter or DM Sans. 6-step scale from 12px to 60px. Weight contrast: 400 body → 700 hero.

**Spacing:** 8px base grid system (4/8/12/16/20/24/32/40/48/64/80/96px).

### 1.3 — Component Library Build

Core components (all with skeleton loader variants):

| Component | Notes |
|-----------|-------|
| MovieCard | Poster, title, year, genre tags. Netflix-style delayed hover expand (300ms delay → 1.3x scale, metadata reveal) |
| MovieCardExpanded | Full detail overlay: synopsis, cast, streaming links, match score |
| Button | Primary (accent gradient), secondary, ghost, icon variants |
| Input / Textarea | Dark surface, subtle border, accent focus ring |
| Chip / Tag | Genre/mood pills with selection animation (expanding circle fill) |
| Avatar / AvatarGroup | Group mode member display |
| Slider | Preference weighting |
| StepIndicator | Onboarding + narrowing flow progress |
| Modal / BottomSheet | Glassmorphism. Desktop: centered modal. Mobile: slide-up bottom sheet with 3 snap points (30/60/95%) |
| ScrollRow | Netflix horizontal scroll with peek pattern (partial next card visible), page-step navigation, left/right chevrons |
| MatchScore | Animated counter (0→final %, 800ms ease-out). Color-coded green/yellow/red |
| Skeleton | Shimmer-animated placeholders for every content component |

### 1.4 — Animation System

| Animation | Implementation |
|-----------|---------------|
| **Card → Detail view** | Framer Motion `layoutId` shared element transition. Poster morphs position + scale + border-radius. 400ms spring. |
| **Card stagger reveal** | Cards enter from bottom: `translateY(20px)→0`, fade in. 70ms stagger delay between cards. |
| **AI Processing** | Canvas constellation visualization: dots scatter → cluster by genre → resolve to final picks. Minimum 3s even if API is faster. |
| **Page transitions** | `AnimatePresence` with opacity + subtle translateY. 300ms. |
| **Match score counter** | `useSpring` counting from 0 to final value. 800ms. |
| **Swipe cards** | Physics-based drag with rotation proportional to horizontal offset. Spring return or velocity-based fly-off. |
| **Reduced motion** | Global `prefers-reduced-motion` support via `MotionConfig reducedMotion="user"`. Replace transforms with opacity fades. |

### 1.5 — Mobile-First Responsive Design

- Design at 375px first, scale up
- Breakpoints: 640 / 768 / 1024 / 1280 / 1536px
- Bottom tab navigation (not hamburger): Home, Search, Group, Watchlist, Profile
- Translucent tab bar with backdrop blur, hide on scroll down
- 2-column card grid on mobile, tap opens bottom sheet
- 44x44px minimum touch targets, 8px minimum spacing between tappable elements
- Lazy load poster images with `srcset` (TMDB `/w185`, `/w342`, `/w500`)

### Deliverables
- [ ] Next.js project with Tailwind + Framer Motion + Radix UI
- [ ] Full design token system (colors, typography, spacing)
- [ ] Component library with all core components
- [ ] Animation system with reduced-motion support
- [ ] Responsive layout with mobile-first bottom navigation
- [ ] Skeleton loaders for every content component

---

## Phase 2: Core User Flows (Weeks 5-8)

**Goal:** Build the complete solo and group recommendation experience.

### 2.1 — Landing Page

- Full-bleed cinematic hero: gradient background, headline "Find the perfect movie — together or solo"
- Two CTAs: "Start Solo" and "Start a Group"
- Feature showcase: 3 scroll-triggered sections (Solo, Group, AI Engine)
- Mobile: stacked layout, full-width CTAs

### 2.2 — Onboarding Flow (First-Time Users)

4-step flow (skippable for returning users):
1. **Mood/vibe selection** — Full-screen grid of mood cards (Thrilling, Cozy, Mind-bending, Feel-good, Dark, Funny, Romantic, Epic). Poster collage backgrounds. Select 1-3.
2. **Genre preferences** — Scrollable chip grid. Tap to select. Minimum 3.
3. **Dealbreakers** — Quick toggles: subtitles OK? Long movies OK? Content rating limit?
4. **Streaming services** — Grid of service logos. Select which you subscribe to.
- Animated transition to results: selected preferences visually "feed into" AI processing animation.

### 2.3 — Solo Recommendation Flow

- **Input screen**: Two modes:
  - Natural language: "I want something like Arrival but scarier"
  - Structured filters: genre chips, decade slider, mood selector, runtime range
- **AI Processing screen**: Constellation animation (3-8 seconds). Status text: "Searching 500,000+ films..." → "Cross-referencing your taste..." → "Found 12 strong matches..."
- **Results screen**: Hero card (large poster, synopsis, match score) + scrollable row of 5 additional picks. Each card expandable.
- **"Narrow it down"**: Tinder-style swipe interface OR side-by-side comparison ("More action-heavy or more cerebral?"). Tournament bracket: 8→4→2→1. Dramatic final reveal with animated match score.

### 2.4 — Group Mode Flow

- **Create session**: Name the session, set your preferences, get a shareable link/code + QR code
- **Join session**: Enter code or tap link. Guest mode (no account needed) or logged-in
- **Preference collection**: Each member privately fills preferences (2 screens max). Progress indicator: "3/5 friends submitted"
- **Waiting room**: Fun stats ("Your group has watched a combined 2,400 movies") while waiting
- **Group results**: Recommendations with "Group Match %" and Venn diagram showing taste overlap. Tags per person showing why each pick works for them.
- **Voting round**: Thumbs up/down on top picks. Real-time results via WebSocket.

### 2.5 — Movie Detail View

Opens as overlay modal (desktop) / bottom sheet (mobile):
- Large backdrop image with gradient fade
- Title, year, runtime, match score with explanation
- Synopsis (collapsible), genre/mood tags
- Director, top 3 cast
- "Where to watch" — streaming service logos with deep links
- Action buttons: "Add to watchlist", "Seen it", "Not interested"

### 2.6 — Session Management

- Conversation state machine: INITIAL → PREFERENCES_GATHERED → CANDIDATES_FETCHED → RECOMMENDATIONS_PRESENTED → REFINING → FINAL_SELECTION
- Condensed context for Claude (structured summary, not raw history) — keeps token count stable
- Redis for active sessions, PostgreSQL for archival

### Deliverables
- [ ] Landing page
- [ ] Onboarding flow (4 steps)
- [ ] Solo mode: input → processing animation → results → narrow-down
- [ ] Group mode: create → invite → collect preferences → results → voting
- [ ] Movie detail modal/bottom sheet
- [ ] Multi-turn conversation with session state machine
- [ ] SSE streaming for recommendation delivery
- [ ] WebSocket for live group sessions

---

## Phase 3: Intelligence & Data Layer (Weeks 8-10)

**Goal:** Make the AI smarter, add personalization, and validate recommendation quality.

### 3.1 — Model Routing

Route requests to the cheapest adequate model:
- **Haiku**: Simple solo, first turn, common preferences (~80% of requests)
- **Sonnet**: Group mode, refinements, complex constraints (~18%)
- **Opus**: Very large groups (5+), internal evaluation (~2%)

Estimated costs at scale:

| Users | Monthly Sessions | Haiku+Sonnet (80/20) | With 20% cache hits |
|-------|-----------------|---------------------|---------------------|
| 1,000 | 8,000 | $147 | $118 |
| 10,000 | 80,000 | $1,472 | $1,178 |
| 100,000 | 800,000 | $14,720 | $11,776 |

### 3.2 — Prompt Caching

Use Anthropic's prompt caching for the system prompt (identical across requests). Reduces input token costs by ~90% for the cached portion.

### 3.3 — Recommendation Pattern Caching

Normalize preferences → hash → cache full recommendation result. Common patterns like "fun comedy on Netflix for date night" will hit cache frequently. Target: 15-25% hit rate.

### 3.4 — User Taste Learning

Build implicit preference model from interaction data:
- Materialized view: genre × user interactions, average ratings, strong positives, dismissal counts
- Bias future TMDB candidate queries toward demonstrated preferences
- Refresh daily

### 3.5 — Recommendation Quality Framework

Curate 50 "golden" test cases with expected/unacceptable outputs. Run weekly evaluation:
- **Precision**: % of recommendations that are acceptable
- **Hallucination rate**: Must be 0% (enforced by candidate-set validation)
- **Constraint adherence**: % matching stated constraints
- **Diversity**: Not just suggesting the same 20 movies
- Alert if any metric degrades >10% week-over-week

### 3.6 — Anti-Hallucination: "Save Me From..." Feature

Let users specify what they're tired of ("Save me from superhero movies, slow burns, love triangles"). Negative preferences are underserved by every competitor — and they build instant trust.

### 3.7 — "Decision Receipt" (Viral Feature)

After a group picks a movie, generate a shareable card: who wanted what, where overlap was, why the AI picked this film. Branded for social sharing (Instagram Stories, iMessage).

### Deliverables
- [ ] Model routing (Haiku/Sonnet/Opus by complexity)
- [ ] Anthropic prompt caching
- [ ] Recommendation pattern cache with normalized keys
- [ ] Implicit taste profile from interaction history
- [ ] Quality evaluation pipeline (50 golden test cases)
- [ ] "Save me from..." negative preference feature
- [ ] Shareable decision receipt

---

## Phase 4: Polish, Accessibility & Testing (Weeks 10-13)

**Goal:** Production-grade quality, accessibility compliance, and comprehensive testing.

### 4.1 — Accessibility Audit

- WCAG AA compliance minimum (4.5:1 contrast for text, 3:1 for large text)
- Full keyboard navigation with roving tabindex on scroll rows
- Screen reader support: semantic HTML, `aria-live` regions for dynamic content, `role="meter"` for match scores
- Focus trapping in modals, skip-to-content link
- `prefers-reduced-motion` globally respected
- Swipe flow has button alternatives for keyboard/switch users
- Test with VoiceOver (macOS/iOS), NVDA (Windows), keyboard-only

### 4.2 — Testing Pyramid

**Unit Tests (target: 80% coverage on business logic)**
- Candidate selection pipeline (TMDB filtering, constraint enforcement)
- Response validation (TMDB ID verification, schema compliance)
- Session state machine transitions
- Rate limiting logic
- Auth token handling

**Integration Tests**
- Full recommendation flow: request → TMDB → Claude (mocked) → validated response
- Auth flows: magic link, OAuth, token refresh
- Group session lifecycle: create → join → preferences → recommend → vote

**E2E Tests (Playwright)**
- Solo flow: landing → preferences → results → detail view → watchlist
- Group flow: create session → share link → both members complete → results
- Mobile viewport tests

**Load Tests (Locust)**
- Mock Claude API, test infrastructure
- Target P95 latency under 100 concurrent users
- Redis memory usage under concurrent sessions

**LLM Integration Tests (nightly, not per-PR)**
- Golden test cases against real Claude API
- Quality regression detection

### 4.3 — Performance Optimization

- Lighthouse score targets: Performance 90+, Accessibility 95+, Best Practices 95+
- Image optimization: TMDB poster WebP conversion, blur placeholder generation via `sharp`
- Bundle splitting: separate chunks for landing, app, and admin
- Lazy loading: routes, heavy components (charts, carousel)
- SSR for landing page (SEO + first paint)

### 4.4 — Error Handling & Edge Cases

- Claude API timeout/failure → graceful degradation with cached/trending fallback
- TMDB API failure → serve from PostgreSQL cache
- Empty results → "Broaden your preferences" guidance
- Extremely conflicting group preferences → compromise pick + rotation suggestion
- Rate limit exceeded → clear messaging with upgrade CTA

### Deliverables
- [ ] WCAG AA accessibility compliance
- [ ] 80%+ unit test coverage on business logic
- [ ] Integration test suite
- [ ] Playwright E2E tests for core flows
- [ ] Locust load testing with results
- [ ] Nightly LLM quality evaluation
- [ ] Lighthouse 90+ performance
- [ ] Graceful degradation for all external service failures

---

## Phase 5: Infrastructure & Launch Prep (Weeks 13-15)

**Goal:** Production infrastructure, monitoring, security hardening, and deployment pipeline.

### 5.1 — Deployment Infrastructure

- **Hosting**: Vercel (frontend) + Railway or Fly.io (backend) or AWS ECS
- **Database**: Managed PostgreSQL (Supabase, Neon, or RDS)
- **Redis**: Managed Redis (Upstash or ElastiCache)
- **CDN**: Vercel Edge Network or CloudFront for static assets
- **Domain + SSL**: Custom domain with automatic HTTPS

### 5.2 — CI/CD Pipeline

- GitHub Actions:
  - PR: lint + type-check + unit tests + integration tests
  - Merge to main: all above + build + deploy to staging
  - Tag release: deploy to production
  - Nightly: LLM quality evaluation + dependency scanning
- Preview deployments for every PR (Vercel)
- Rollback: one-click via deployment platform

### 5.3 — Monitoring & Observability

- **APM**: Sentry (error tracking + performance)
- **Metrics**: Prometheus + Grafana (request latency, error rates, Claude API costs, cache hit rates)
- **Logging**: Structured JSON logs → aggregation service (Axiom, Datadog, or CloudWatch)
- **Alerts**: PagerDuty or OpsGenie for critical failures (API down, error rate spike, cost anomaly)
- **Uptime**: External health check (Better Uptime, Pingdom)

### 5.4 — Security Hardening

- Secrets management: environment variables via deployment platform (not .env files)
- Input sanitization: prevent prompt injection in user messages to Claude
- CORS: whitelist production domains only
- Helmet.js / security headers
- Dependency scanning: Dependabot + Snyk
- Rate limiting: per-user (authenticated) + per-IP (unauthenticated)
- Audit logging: who called what endpoint when (append-only log)

### 5.5 — Analytics

- **PostHog** or **Mixpanel** for product analytics:
  - Funnel: landing → onboarding → first recommendation → second session
  - Retention: D1, D7, D30
  - Feature usage: solo vs group, natural language vs filters, narrow-down completion
- **Custom dashboard**: recommendation quality metrics, API costs, cache performance

### Deliverables
- [ ] Production deployment pipeline (staging + production)
- [ ] Managed PostgreSQL + Redis
- [ ] Sentry error tracking
- [ ] Prometheus/Grafana metrics dashboard
- [ ] Structured logging with aggregation
- [ ] Security headers + dependency scanning + audit logging
- [ ] PostHog analytics integration
- [ ] Custom operations dashboard

---

## Phase 6: Launch (Weeks 15-16)

**Goal:** Ship it, get the first 1,000 users, and establish feedback loops.

### 6.1 — Pre-Launch Checklist

- [ ] All critical flows tested on iOS Safari, Android Chrome, desktop Chrome/Firefox/Safari
- [ ] Load test passed: 100 concurrent users, P95 < 2s for recommendations
- [ ] Hallucination rate verified at 0% across golden test suite
- [ ] WCAG AA accessibility audit passed
- [ ] Privacy policy + Terms of Service published
- [ ] Analytics tracking verified for all key events
- [ ] Error alerting tested (trigger a test alert)
- [ ] Rollback procedure documented and tested
- [ ] Seed data: trending movies, streaming availability cached

### 6.2 — Launch Channels

| Channel | Tactic | Expected Users |
|---------|--------|---------------|
| **Product Hunt** | Tuesday/Wednesday launch, compelling tagline, demo video | 300-800 |
| **Reddit** | r/movies, r/MovieSuggestions, r/netflix — "I built this" framing | 200-500 |
| **Twitter/X** | 60-second demo videos, tag film critics | 100-300 |
| **Film podcasts** | Mid-tier podcasts (10K-50K listeners) | 100-200 |
| **Personal network** | 50 friends use it on Friday, share results | 50-100 |

### 6.3 — Post-Launch Feedback Loop

- In-app: "Did you watch it? How was it?" — two-tap post-watch rating
- Weekly email: "Your personalized pick this week" — one curated recommendation
- NPS survey at day 7 and day 30
- Monitor: session completion rate (target >80%), re-roll rate (target <30%), return within 7 days (target >25%)

### 6.4 — North Star Metrics

| Metric | Launch Target (Month 1) | Scale Target (Month 6) |
|--------|------------------------|----------------------|
| Weekly Active Users | 500 | 5,000 |
| Decisions Completed/Week | 200 | 3,000 |
| Group Sessions/Week | 50 | 500 |
| Session Completion Rate | >80% | >85% |
| Post-Watch Satisfaction (thumbs up) | >70% | >80% |
| Cost per Recommendation | <$0.05 | <$0.03 |
| Hallucination Rate | 0% | 0% |

---

## Monetization (Post-Launch)

### Free Tier
- 5 solo recommendations/day, 2 group sessions/week
- Single "Sponsored Pick" in results (clearly labeled)

### FilmMatch Pro ($3.99/mo or $29.99/yr)
- Unlimited recommendations + group sessions
- Persistent taste profile + watch history
- Priority AI processing
- No sponsored picks

### Affiliate Revenue (All Tiers)
- Deep links to streaming services via JustWatch/Watchmode
- $0.10-0.50 per click-through
- Highest passive revenue potential at scale

### Conservative Year 1 Projection (at 50K users)
- Pro subscriptions (2% conversion): $30,000
- Affiliate clicks (20% click-through): $24,000
- Sponsored picks: $6,000
- **Total: ~$60,000**

---

## Risk Mitigation

| Risk | Severity | Mitigation |
|------|----------|------------|
| AI hallucination | Critical | Candidate-set pattern — Claude ranks verified TMDB data, never generates from memory |
| Stale streaming data | High | Weekly refresh + "availability may vary" disclaimer |
| API costs at scale | High | Model routing (Haiku 80%), prompt caching, response caching, rate limits on free tier |
| Low retention | High | Group mode (recurring social use case), weekly email, post-watch feedback loop |
| Single LLM dependency | Medium | Abstract LLM layer for provider swapping |
| Competitor response | Medium | Move fast, own "group decision" brand, build taste data moat |

---

## Timeline Summary

| Phase | Weeks | Focus | Key Milestone |
|-------|-------|-------|---------------|
| **0** | 1-2 | Foundation | Hybrid AI pipeline + DB + Auth + API |
| **1** | 3-5 | Design System | Netflix-quality component library + animations |
| **2** | 5-8 | Core Flows | Solo + Group + Narrow-down fully functional |
| **3** | 8-10 | Intelligence | Model routing, caching, taste learning, quality eval |
| **4** | 10-13 | Polish | Accessibility, testing, performance, error handling |
| **5** | 13-15 | Infrastructure | Deployment, monitoring, security, analytics |
| **6** | 15-16 | Launch | Ship, first 1,000 users, feedback loops |

**Total: ~16 weeks to launch-ready product.**

---

## Architecture Diagram

```
                        ┌──────────────┐
                        │   Frontend   │
                        │  (Next.js)   │
                        └──────┬───────┘
                               │
                    ┌──────────┼──────────┐
                    │     FastAPI Gateway  │
                    │  (Auth, Rate Limit,  │
                    │   Logging, Routing)  │
                    └──────────┬───────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
    ┌─────┴─────┐     ┌───────┴───────┐    ┌───────┴────────┐
    │ TMDB API  │     │ Claude API    │    │ Watchmode API  │
    │ (movies,  │     │ (rank, reason,│    │ (streaming     │
    │  search,  │     │  converse)    │    │  availability) │
    │  trending)│     └───────────────┘    └────────────────┘
    └───────────┘
          │                    │                    │
          └────────────────────┼────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │     PostgreSQL      │
                    │  (users, movies,    │
                    │   sessions, history)│
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    │       Redis         │
                    │  (sessions, cache,  │
                    │   rate limits)      │
                    └─────────────────────┘
```

---

*This plan was assembled from four specialist reviews: Architecture, AI/Backend, UI/UX, and Product Strategy.*
