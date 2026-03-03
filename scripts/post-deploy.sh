#!/usr/bin/env bash
# Post-deploy script — run after deploying to Railway
# Usage: BACKEND_URL=https://your-backend.railway.app ./scripts/post-deploy.sh
set -euo pipefail

BACKEND_URL="${BACKEND_URL:?BACKEND_URL environment variable required}"

echo "==> Health check..."
curl -sf "$BACKEND_URL/api/v1/health" | python3 -m json.tool

echo ""
echo "==> Running cache warmup (trending movies)..."
curl -sf -X POST "$BACKEND_URL/api/v1/ops/warmup" | python3 -m json.tool

echo ""
echo "==> Triggering movie catalog sync..."
curl -sf -X POST "$BACKEND_URL/api/v1/ops/sync-movies" | python3 -m json.tool

echo ""
echo "==> Launch readiness check..."
curl -sf "$BACKEND_URL/api/v1/ops/launch-check" | python3 -m json.tool

echo ""
echo "==> Post-deploy complete!"
