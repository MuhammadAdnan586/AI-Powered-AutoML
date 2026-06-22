"""
Module 2 - Additional Database Models
TrainingSession and ModelResult only.
ProcessedDataset and EngineeredDataset are defined in app.datasets.models
"""

from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base
from app.datasets.models import ProcessedDataset, EngineeredDataset


class TrainingSession(Base):
    """Stores AutoML training session results."""
    __tablename__ = "training_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    dataset_id = Column(Integer, ForeignKey("engineered_datasets.id"), nullable=False)
    target_column = Column(String(200))
    problem_type = Column(String(50))
    best_model = Column(String(100))
    best_score = Column(Float)
    results = Column(Text)
    status = Column(String(50), default="pending")
    hyperparameter_tuning = Column(Boolean, default=False)
    test_size = Column(Float, default=0.2)
    mlflow_run_id = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    model_results = relationship("ModelResult", back_populates="training_session")


class ModelResult(Base):
    """Stores individual model training results for a session."""
    __tablename__ = "model_results"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("training_sessions.id"), nullable=False)
    model_name = Column(String(100), nullable=False)
    display_name = Column(String(100))
    category = Column(String(50))
    rank = Column(Integer)

    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    roc_auc = Column(Float)

    r2_score = Column(Float)
    mae = Column(Float)
    mse = Column(Float)
    rmse = Column(Float)

    training_time_seconds = Column(Float)
    cv_mean = Column(Float)
    cv_std = Column(Float)
    best_params = Column(Text)
    hyperparameter_tuned = Column(Boolean, default=False)
    status = Column(String(20), default="success")
    error_message = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    training_session = relationship("TrainingSession", back_populates="model_results")