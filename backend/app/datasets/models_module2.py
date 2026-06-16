"""
Module 2 - Additional Database Models
Add these to existing models or merge with Module 1 models file
"""

from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database.base import Base


class ProcessedDataset(Base):
    """Stores preprocessing results."""
    __tablename__ = "processed_datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    original_dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    file_path = Column(String(500), nullable=False)
    target_column = Column(String(200))
    preprocessing_config = Column(Text)
    preprocessing_report = Column(Text)
    rows = Column(Integer)
    columns = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    original_dataset = relationship("Dataset", back_populates="processed_datasets")
    engineered_datasets = relationship("EngineeredDataset", back_populates="processed_dataset")


class EngineeredDataset(Base):
    """Stores feature engineering results."""
    __tablename__ = "engineered_datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    processed_dataset_id = Column(Integer, ForeignKey("processed_datasets.id"), nullable=False)
    file_path = Column(String(500), nullable=False)
    target_column = Column(String(200))
    fe_config = Column(Text)
    fe_report = Column(Text)
    rows = Column(Integer)
    columns = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    processed_dataset = relationship("ProcessedDataset", back_populates="engineered_datasets")
    training_sessions = relationship("TrainingSession", back_populates="engineered_dataset")


class TrainingSession(Base):
    """Stores AutoML training session results."""
    __tablename__ = "training_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    dataset_id = Column(Integer, ForeignKey("engineered_datasets.id"), nullable=False)
    target_column = Column(String(200))
    problem_type = Column(String(50))  # classification / regression
    best_model = Column(String(100))
    best_score = Column(Float)
    results = Column(Text)  # JSON string of full results
    status = Column(String(50), default="pending")  # pending, training, completed, failed
    hyperparameter_tuning = Column(Boolean, default=False)
    test_size = Column(Float, default=0.2)
    mlflow_run_id = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    engineered_dataset = relationship("EngineeredDataset", back_populates="training_sessions")
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
    
    # Classification metrics
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    roc_auc = Column(Float)
    
    # Regression metrics
    r2_score = Column(Float)
    mae = Column(Float)
    mse = Column(Float)
    rmse = Column(Float)
    
    # Training info
    training_time_seconds = Column(Float)
    cv_mean = Column(Float)
    cv_std = Column(Float)
    best_params = Column(Text)  # JSON
    hyperparameter_tuned = Column(Boolean, default=False)
    status = Column(String(20), default="success")
    error_message = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    training_session = relationship("TrainingSession", back_populates="model_results")
