"""
Retraining Schedule – SQLAlchemy ORM
Stores cron-based retraining jobs per model.
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database.base import Base


class RetrainingStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class RetrainingSchedule(Base):
    __tablename__ = "retraining_schedules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    model_id = Column(Integer, ForeignKey("model_registry.id"), nullable=False)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)

    cron_expression = Column(String(50), nullable=False)   # e.g. "0 2 * * *"
    is_active = Column(Boolean, default=True)

    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    last_status = Column(String(20), default=RetrainingStatus.PENDING)
    last_error = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    model = relationship("ModelRegistry")
    dataset = relationship("Dataset")


class RetrainingLog(Base):
    __tablename__ = "retraining_logs"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("retraining_schedules.id"), nullable=False)
    status = Column(String(20), nullable=False)
    accuracy_before = Column(String(10), nullable=True)
    accuracy_after = Column(String(10), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    triggered_at = Column(DateTime, default=datetime.utcnow)

    schedule = relationship("RetrainingSchedule")
