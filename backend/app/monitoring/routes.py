"""
Module 4 – Monitoring
Health check, system metrics, endpoint usage stats.
"""

import psutil
import platform
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.rbac.dependencies import is_admin
from app.users.models import User

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Public health endpoint – used by Docker HEALTHCHECK and load balancers.
    Returns 200 if the app + DB are reachable.
    """
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {e}"

    return {
        "status": "healthy" if db_status == "ok" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status,
    }


@router.get("/metrics")
def system_metrics(_admin: User = Depends(is_admin)):
    """
    Admin-only: real-time system resource usage.
    """
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    cpu_percent = psutil.cpu_percent(interval=0.5)

    return {
        "cpu": {
            "percent": cpu_percent,
            "cores": psutil.cpu_count(logical=True),
        },
        "memory": {
            "total_gb": round(mem.total / 1e9, 2),
            "used_gb": round(mem.used / 1e9, 2),
            "percent": mem.percent,
        },
        "disk": {
            "total_gb": round(disk.total / 1e9, 2),
            "used_gb": round(disk.used / 1e9, 2),
            "percent": disk.percent,
        },
        "platform": platform.system(),
        "python_version": platform.python_version(),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/api-stats")
def api_usage_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Per-user API endpoint usage summary.
    """
    from app.api_generator.models import ApiEndpoint

    endpoints = (
        db.query(ApiEndpoint)
        .filter_by(user_id=current_user.id)
        .all()
    )
    return [
        {
            "endpoint": ep.endpoint_name,
            "slug": ep.slug,
            "total_calls": ep.total_calls,
            "last_called_at": ep.last_called_at,
            "is_active": ep.is_active,
        }
        for ep in endpoints
    ]


@router.get("/model-stats")
def model_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Summary of all models + retraining history for the current user.
    """
    from app.model_registry.models import ModelRegistry
    from app.retraining.models import RetrainingSchedule

    models = db.query(ModelRegistry).filter_by(user_id=current_user.id).all()
    schedules = db.query(RetrainingSchedule).filter_by(user_id=current_user.id).all()

    return {
        "total_models": len(models),
        "models": [
            {
                "id": m.id,
                "name": m.model_name,
                "accuracy": m.accuracy,
                "version": m.version,
                "created_at": m.created_at,
            }
            for m in models
        ],
        "retraining_schedules": len(schedules),
        "active_schedules": sum(1 for s in schedules if s.is_active),
    }
