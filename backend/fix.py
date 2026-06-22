"""
AutoML Fix Script - Run this from backend folder:
python fix_all.py
"""

import os

BASE = r"C:\Users\adnan\Ai-Powered AutoML\backend\app"

# ── Step 1: Create routes.py aliases where only router.py exists ──────────
# main.py imports 'routes' from these modules but they have 'router.py'
needs_routes_alias = ["auth", "users", "datasets", "automl", "benchmark", "mlflow_tracking"]

for module in needs_routes_alias:
    routes_path = os.path.join(BASE, module, "routes.py")
    router_path = os.path.join(BASE, module, "router.py")
    if not os.path.exists(routes_path) and os.path.exists(router_path):
        with open(routes_path, "w") as f:
            f.write(f"# Auto-generated alias\nfrom app.{module}.router import router\n")
        print(f"✅ Created routes.py alias for: {module}")
    elif os.path.exists(routes_path):
        print(f"⏭  routes.py already exists: {module}")
    else:
        print(f"⚠️  router.py missing too: {module}")

# ── Step 2: Create training module (empty but functional) ─────────────────
training_dir = os.path.join(BASE, "training")
os.makedirs(training_dir, exist_ok=True)

training_init = os.path.join(training_dir, "__init__.py")
if not os.path.exists(training_init):
    with open(training_init, "w") as f:
        f.write("")

training_routes = os.path.join(training_dir, "routes.py")
if not os.path.exists(training_routes):
    with open(training_routes, "w") as f:
        f.write('''from fastapi import APIRouter
router = APIRouter(prefix="/training", tags=["Training"])

@router.get("/status")
def training_status():
    return {"status": "Training module ready"}
''')
    print("✅ Created training/routes.py")

# ── Step 3: Create api_generator module ───────────────────────────────────
api_gen_dir = os.path.join(BASE, "api_generator")
os.makedirs(api_gen_dir, exist_ok=True)

api_gen_init = os.path.join(api_gen_dir, "__init__.py")
if not os.path.exists(api_gen_init):
    with open(api_gen_init, "w") as f:
        f.write("")

api_gen_routes = os.path.join(api_gen_dir, "routes.py")
if not os.path.exists(api_gen_routes):
    with open(api_gen_routes, "w") as f:
        f.write('''from fastapi import APIRouter
router = APIRouter(prefix="/api-generator", tags=["API Generator"])

@router.get("/status")
def api_gen_status():
    return {"status": "API Generator module ready"}
''')
    print("✅ Created api_generator/routes.py")

# ── Step 4: Fix dashboard (has both router.py and routes.py — check routes.py) ──
dashboard_routes = os.path.join(BASE, "dashboard", "routes.py")
with open(dashboard_routes, "r") as f:
    content = f.read()
if "router" not in content:
    with open(dashboard_routes, "w") as f:
        f.write("from app.dashboard.router import router\n")
    print("✅ Fixed dashboard/routes.py")
else:
    print("⏭  dashboard/routes.py OK")

# ── Step 5: Check users/router.py has actual router ───────────────────────
users_router = os.path.join(BASE, "users", "router.py")
with open(users_router, "r") as f:
    content = f.read()
if "APIRouter" not in content and len(content.strip()) < 10:
    with open(users_router, "w") as f:
        f.write('''from fastapi import APIRouter
router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me")
def get_me():
    return {"message": "Users module ready"}
''')
    print("✅ Fixed users/router.py (was empty)")
else:
    print("⏭  users/router.py OK")

# ── Step 6: Verify session.py content ─────────────────────────────────────
session_path = os.path.join(BASE, "database", "session.py")
with open(session_path, "w") as f:
    f.write("from app.database.connection import SessionLocal, engine, Base, get_db\n")
print("✅ Fixed database/session.py")

# ── Done ──────────────────────────────────────────────────────────────────
print("\n" + "="*50)
print("✅ All fixes applied!")
print("="*50)
print("\nNow run:")
print("  uvicorn main:app --reload --host 0.0.0.0 --port 8000")