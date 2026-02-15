"""Prometheus metrics for FilmMatch AI."""

from prometheus_client import Counter, Histogram

# Recommendation metrics
RECOMMENDATIONS_TOTAL = Counter(
    "filmmatch_recommendations_total",
    "Total recommendation requests",
    ["mode", "model", "complexity_tier"],
)

RECOMMENDATION_LATENCY = Histogram(
    "filmmatch_recommendation_latency_seconds",
    "Recommendation generation latency",
    ["mode"],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
)

# Claude API metrics
CLAUDE_REQUESTS_TOTAL = Counter(
    "filmmatch_claude_requests_total",
    "Total Claude API calls",
    ["model", "status"],
)

CLAUDE_FALLBACK_TOTAL = Counter(
    "filmmatch_claude_fallback_total",
    "Times Claude API failed and fallback was used",
)

# TMDB metrics
TMDB_REQUESTS_TOTAL = Counter(
    "filmmatch_tmdb_requests_total",
    "Total TMDB API calls",
    ["endpoint", "status"],
)

TMDB_CACHE_HITS = Counter(
    "filmmatch_tmdb_cache_hits_total",
    "TMDB cache hits",
)

TMDB_CACHE_MISSES = Counter(
    "filmmatch_tmdb_cache_misses_total",
    "TMDB cache misses",
)

# Auth metrics
AUTH_EVENTS = Counter(
    "filmmatch_auth_events_total",
    "Authentication events",
    ["action"],
)

# Rate limit metrics
RATE_LIMIT_HITS = Counter(
    "filmmatch_rate_limit_hits_total",
    "Requests rejected by rate limiting",
    ["route"],
)
