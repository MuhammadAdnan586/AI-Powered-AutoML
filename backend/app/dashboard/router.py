"""
Dashboard Router
GET /dashboard/stats  — Summary stats for the logged-in user
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta, timezone

from app.database.connection import get_db
from app.auth.models import User
from app.auth.dependencies import get_current_user
from app.datasets.models import Dataset, DatasetStatus

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


class DashboardStats(BaseModel):
    total_datasets: int
    ready_datasets: int
    processing_datasets: int
    error_datasets: int
    total_storage_bytes: int
    total_rows: int
    recent_datasets: list
    user_since_days: int


class RecentDataset(BaseModel):
    id: int
    name: str
    status: str
    row_count: Optional[int]
    column_count: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get summary statistics for the current user's dashboard.
    Includes dataset counts, storage usage, and recent activity.
    """
    # Base query for this user's datasets
    base = db.query(Dataset).filter(Dataset.owner_id == current_user.id)

    total = base.count()
    ready = base.filter(Dataset.status == DatasetStatus.ready).count()
    processing = base.filter(Dataset.status == DatasetStatus.processing).count()
    error = base.filter(Dataset.status == DatasetStatus.error).count()

    # Storage used
    storage_result = db.query(func.sum(Dataset.file_size_bytes)).filter(
        Dataset.owner_id == current_user.id
    ).scalar()
    total_storage = int(storage_result or 0)

    # Total rows across all datasets
    rows_result = db.query(func.sum(Dataset.row_count)).filter(
        Dataset.owner_id == current_user.id
    ).scalar()
    total_rows = int(rows_result or 0)

    # Recent 5 datasets
    recent = (
        db.query(Dataset)
        .filter(Dataset.owner_id == current_user.id)
        .order_by(Dataset.created_at.desc())
        .limit(5)
        .all()
    )
    recent_list = [
        {
            "id": d.id,
            "name": d.name,
            "status": d.status.value,
            "row_count": d.row_count,
            "column_count": d.column_count,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in recent
    ]

    # Days since registration
    user_since_days = 0
    if current_user.created_at:
        delta = datetime.now(timezone.utc) - current_user.created_at.replace(tzinfo=timezone.utc)
        user_since_days = delta.days

    return DashboardStats(
        total_datasets=total,
        ready_datasets=ready,
        processing_datasets=processing,
        error_datasets=error,
        total_storage_bytes=total_storage,
        total_rows=total_rows,
        recent_datasets=recent_list,
        user_since_days=user_since_days,
    )
