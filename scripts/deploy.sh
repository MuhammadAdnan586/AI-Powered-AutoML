#!/usr/bin/env bash
# ══════════════════════════════════════════════════════
#  AutoML SaaS – Deployment Script (Module 4)
#  Usage: ./scripts/deploy.sh [--prod]
# ══════════════════════════════════════════════════════

set -euo pipefail

PROD=false
[[ "${1:-}" == "--prod" ]] && PROD=true

echo "======================================================"
echo "  AutoML SaaS Deployment"
echo "  Mode: $( $PROD && echo 'PRODUCTION' || echo 'DEVELOPMENT' )"
echo "======================================================"

# ── Pre-checks ────────────────────────────────────────
if [ ! -f ".env" ]; then
    echo "⚠  .env not found. Copying from .env.example …"
    cp .env.example .env
    echo "📝 Please fill in your .env values then re-run this script."
    exit 1
fi

# ── Pull latest code ───────────────────────────────────
if $PROD; then
    echo "📥 Pulling latest code …"
    git pull origin main
fi

# ── Build images ───────────────────────────────────────
echo "🔨 Building Docker images …"
docker compose build --no-cache

# ── Database migrations ────────────────────────────────
echo "🗄  Running Alembic migrations …"
docker compose run --rm backend alembic upgrade head

# ── Start all services ────────────────────────────────
echo "🚀 Starting services …"
docker compose up -d

# ── Health check ──────────────────────────────────────
echo "⏳ Waiting for backend to be healthy …"
for i in {1..30}; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is healthy!"
        break
    fi
    sleep 2
    [ "$i" -eq 30 ] && echo "❌ Backend health check timed out" && exit 1
done

echo ""
echo "════════════════════════════════════════════════════"
echo "  ✅ AutoML SaaS is running!"
echo "  Frontend : http://localhost"
echo "  API      : http://localhost:8000/api/v1"
echo "  API Docs : http://localhost:8000/docs"
echo "  MLflow   : http://localhost:5000"
echo "════════════════════════════════════════════════════"
