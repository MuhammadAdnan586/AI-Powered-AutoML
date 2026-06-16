"""
Module 4 – Scheduled Retraining (Cron Jobs)
Create, manage, and trigger retraining schedules for ML models.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.users.models import User
from app.retraining.service import RetrainingService
from app.retraining.schemas import (
    ScheduleCreate,
    ScheduleResponse,
    RetrainingLogResponse,
)

router = APIRouter(prefix="/retraining", tags=["Scheduled Retraining"])


@router.post("/schedule", response_model=ScheduleResponse)
def create_schedule(
    payload: ScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new cron-based retraining schedule for a model."""
    service = RetrainingService(db)
    return service.create_schedule(payload, user_id=current_user.id)


@router.get("/schedules", response_model=List[ScheduleResponse])
def list_schedules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RetrainingService(db)
    return service.list_schedules(user_id=current_user.id)


@router.patch("/schedule/{schedule_id}/toggle")
def toggle_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Activate or deactivate a retraining schedule."""
    service = RetrainingService(db)
    sched = service.toggle(schedule_id, current_user.id)
    return {"detail": f"Schedule {'activated' if sched.is_active else 'deactivated'}"}


@router.post("/schedule/{schedule_id}/trigger")
def trigger_now(
    schedule_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually trigger a retraining job right now (runs in background)."""
    service = RetrainingService(db)
    background_tasks.add_task(service.run_retraining, schedule_id, current_user.id)
    return {"detail": "Retraining job queued. You will be notified on completion."}


@router.get("/schedule/{schedule_id}/logs", response_model=List[RetrainingLogResponse])
def get_logs(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RetrainingService(db)
    return service.get_logs(schedule_id, current_user.id)


@router.delete("/schedule/{schedule_id}")
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RetrainingService(db)
    service.delete_schedule(schedule_id, current_user.id)
    return {"detail": "Schedule deleted"}
