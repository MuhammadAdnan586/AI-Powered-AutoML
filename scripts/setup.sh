#!/bin/bash
# ============================================================
# AutoML SaaS - Local Development Setup Script
# Run this once to set up your development environment
# ============================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   AutoML SaaS - Setup Script          ${NC}"
echo -e "${BLUE}========================================${NC}"

# ── 1. Check prerequisites ──────────────────────────────────
echo -e "\n${YELLOW}[1/5] Checking prerequisites...${NC}"
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 required"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js required"; exit 1; }
command -v mysql >/dev/null 2>&1 || { echo "⚠️  MySQL not found — install it or use Docker"; }
echo -e "${GREEN}✅ Prerequisites checked${NC}"

# ── 2. Copy .env if not exists ─────────────────────────────
echo -e "\n${YELLOW}[2/5] Setting up environment files...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env 2>/dev/null || echo "⚠️  No .env.example found, update .env manually"
    echo -e "${GREEN}✅ .env created — please update DB credentials${NC}"
else
    echo "   .env already exists"
fi

if [ ! -f "frontend/.env.local" ]; then
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > frontend/.env.local
    echo -e "${GREEN}✅ frontend/.env.local created${NC}"
fi

# ── 3. Backend Python setup ─────────────────────────────────
echo -e "\n${YELLOW}[3/5] Setting up Python backend...${NC}"
cd backend
python3 -m venv venv 2>/dev/null || echo "   venv already exists"
source venv/bin/activate
pip install -r requirements.txt --quiet
echo -e "${GREEN}✅ Python dependencies installed${NC}"

# Create upload directories
mkdir -p uploads models artifacts logs
echo -e "${GREEN}✅ Backend directories created${NC}"
cd ..

# ── 4. Frontend Node setup ──────────────────────────────────
echo -e "\n${YELLOW}[4/5] Setting up Next.js frontend...${NC}"
cd frontend
npm install --silent
echo -e "${GREEN}✅ Node.js dependencies installed${NC}"
cd ..

# ── 5. Database migration ───────────────────────────────────
echo -e "\n${YELLOW}[5/5] Database migration...${NC}"
echo -e "   Run this after setting up MySQL:"
echo -e "   ${BLUE}cd backend && source venv/bin/activate${NC}"
echo -e "   ${BLUE}alembic upgrade head${NC}"

# ── Done ────────────────────────────────────────────────────
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}   ✅ Setup Complete!                   ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Start backend:  ${BLUE}cd backend && source venv/bin/activate && uvicorn app.main:app --reload${NC}"
echo -e "Start frontend: ${BLUE}cd frontend && npm run dev${NC}"
echo -e "API Docs:       ${BLUE}http://localhost:8000/docs${NC}"
echo -e "Frontend:       ${BLUE}http://localhost:3000${NC}"
echo ""
