from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ScheduleCreate(BaseModel):
    model_id: int
    dataset_id: int
    cron_expression: str  # "0 2 * * *" = every day at 2 AM


class ScheduleResponse(BaseModel):
    id: int
    model_id: int
    dataset_id: int
    cron_expression: str
    is_active: bool
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    last_status: str
    created_at: datetime

    class Config:
        from_attributes = True


class RetrainingLogResponse(BaseModel):
    id: int
    schedule_id: int
    status: str
    accuracy_before: Optional[str]
    accuracy_after: Optional[str]
    duration_seconds: Optional[int]
    error_message: Optional[str]
    triggered_at: datetime

    class Config:
        from_attributes = True
