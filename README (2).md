# Module 4 – Production & SaaS Features

Complete implementation of all production features for the AutoML SaaS platform.

---

## Features Implemented

| Feature | Location |
|---|---|
| ✅ No-Code REST API Generator | `app/api_generator/` |
| ✅ One-Click Model Deployment | `app/api_generator/service.py` |
| ✅ Scheduled Retraining (Cron Jobs) | `app/retraining/` + `app/scheduler/` |
| ✅ Email Notifications | `app/notifications/service.py` |
| ✅ In-App Notifications | `app/notifications/` |
| ✅ Docker Deployment | `docker/`, `docker-compose.yml` |
| ✅ Background Jobs (APScheduler) | `app/scheduler/jobs.py` |
| ✅ Monitoring & Health Check | `app/monitoring/routes.py` |
| ✅ Structured JSON Logging | `app/logs_module/` |
| ✅ Role-Based Access Control | `app/rbac/` |
| ✅ Security (Rate limit, Headers, CORS) | `app/security/middleware.py` |
| ✅ Nginx Reverse Proxy + SSL | `nginx/nginx.conf` |

---

## Folder Structure

```
module4/
├── backend/
│   ├── main.py                         ← FastAPI app entry point
│   └── app/
│       ├── api_generator/              ← No-code REST API generator
│       │   ├── models.py
│       │   ├── schemas.py
│       │   ├── service.py
│       │   └── routes.py
│       ├── retraining/                 ← Scheduled retraining
│       │   ├── models.py
│       │   ├── schemas.py
│       │   ├── service.py
│       │   └── routes.py
│       ├── notifications/              ← Email + in-app notifications
│       │   ├── models.py
│       │   ├── schemas.py
│       │   ├── service.py
│       │   └── routes.py
│       ├── rbac/                       ← Role-Based Access Control
│       │   ├── models.py
│       │   ├── schemas.py
│       │   ├── dependencies.py
│       │   └── routes.py
│       ├── scheduler/                  ← APScheduler cron jobs
│       │   └── jobs.py
│       ├── monitoring/                 ← Health check + metrics
│       │   └── routes.py
│       ├── logs_module/                ← Structured logging
│       │   ├── logger.py
│       │   └── middleware.py
│       ├── security/                   ← Rate limiting + security headers
│       │   └── middleware.py
│       └── config/
│           └── settings.py
├── docker/
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
├── nginx/
│   └── nginx.conf
├── scripts/
│   ├── deploy.sh
│   └── init.sql
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## Quick Start

### 1. Setup environment
```bash
cp .env.example .env
# Edit .env with your SMTP credentials, DB password, SECRET_KEY
```

### 2. Deploy with Docker
```bash
bash scripts/deploy.sh
```

### 3. Access the platform
| Service | URL |
|---|---|
| Frontend | http://localhost |
| API Docs | http://localhost:8000/docs |
| MLflow | http://localhost:5000 |

---

## API Endpoints (Module 4)

### No-Code API Generator
```
POST   /api/v1/api-generator/generate           ← Generate REST API for a model
GET    /api/v1/api-generator/list               ← List your endpoints
POST   /api/v1/api-generator/{id}/regenerate-key
DELETE /api/v1/api-generator/{id}
POST   /api/v1/api-generator/predict/{slug}     ← Public prediction (API key auth)
```

### Scheduled Retraining
```
POST   /api/v1/retraining/schedule              ← Create cron schedule
GET    /api/v1/retraining/schedules             ← List schedules
PATCH  /api/v1/retraining/schedule/{id}/toggle  ← Enable/disable
POST   /api/v1/retraining/schedule/{id}/trigger ← Manual trigger
GET    /api/v1/retraining/schedule/{id}/logs    ← View logs
```

### Notifications
```
GET    /api/v1/notifications/             ← Get all (or ?unread_only=true)
PATCH  /api/v1/notifications/{id}/read
PATCH  /api/v1/notifications/mark-all-read
DELETE /api/v1/notifications/{id}
```

### RBAC (Admin only)
```
POST   /api/v1/rbac/roles                 ← Create role
GET    /api/v1/rbac/roles
POST   /api/v1/rbac/assign                ← Assign role to user
DELETE /api/v1/rbac/revoke
POST   /api/v1/rbac/permissions
```

### Monitoring
```
GET    /api/v1/monitoring/health          ← Public health check
GET    /api/v1/monitoring/metrics         ← Admin: CPU/RAM/Disk
GET    /api/v1/monitoring/api-stats       ← API usage stats
GET    /api/v1/monitoring/model-stats     ← Model + retraining summary
```

---

## Using the API Generator (Example)

```python
import requests

# 1. Generate API endpoint for model ID 5
r = requests.post(
    "http://localhost:8000/api/v1/api-generator/generate",
    headers={"Authorization": "Bearer <your-jwt-token>"},
    json={"model_id": 5, "endpoint_name": "churn-predictor"}
)
data = r.json()
slug = data["slug"]
api_key = data["api_key"]

# 2. Call the public prediction endpoint (no login needed)
prediction = requests.post(
    f"http://localhost:8000/api/v1/api-generator/predict/{slug}",
    headers={"X-API-Key": api_key},
    json={"features": {"age": 35, "tenure": 12, "monthly_charges": 65.5}}
)
print(prediction.json())
# {"prediction": 0, "probability": [0.82, 0.18], "model_name": "XGBoost", ...}
```

---

## RBAC Usage in Routes

```python
from app.rbac.dependencies import require_role, require_permission

@router.delete("/model/{id}")
def delete_model(id: int, current_user = Depends(require_role("admin"))):
    ...

@router.post("/train")
def train(current_user = Depends(require_permission("models", "write"))):
    ...
```

---

## Cron Expression Reference

| Expression | Meaning |
|---|---|
| `0 2 * * *` | Every day at 2:00 AM |
| `0 */6 * * *` | Every 6 hours |
| `0 0 * * 0` | Every Sunday at midnight |
| `*/30 * * * *` | Every 30 minutes |
