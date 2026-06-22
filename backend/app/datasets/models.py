"""
Dataset Models
Dataset: stores metadata for uploaded files
DatasetVersion: v1, v2, v3 versioning per dataset
"""
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    Text, Enum, ForeignKey, BigInteger, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base
import enum


class DatasetStatus(str, enum.Enum):
    uploading = "uploading"
    processing = "processing"
    ready = "ready"
    error = "error"


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(DatasetStatus), default=DatasetStatus.uploading)
    original_filename = Column(String(500), nullable=False)
    file_extension = Column(String(10), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=True)
    row_count = Column(Integer, nullable=True)
    column_count = Column(Integer, nullable=True)
    column_names = Column(JSON, nullable=True)
    dtypes_info = Column(JSON, nullable=True)
    missing_values_info = Column(JSON, nullable=True)
    preview_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="datasets")
    versions = relationship("DatasetVersion", back_populates="dataset", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Dataset(id={self.id}, name={self.name}, owner={self.owner_id})>"


class DatasetVersion(Base):
    __tablename__ = "dataset_versions"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False, default=1)
    version_label = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    file_path = Column(String(1000), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=True)
    row_count = Column(Integer, nullable=True)
    column_count = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    dataset = relationship("Dataset", back_populates="versions")

    def __repr__(self):
        return f"<DatasetVersion(dataset={self.dataset_id}, v={self.version_number})>"


class ProcessedDataset(Base):
    __tablename__ = "processed_datasets"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    version_id = Column(Integer, ForeignKey("dataset_versions.id"), nullable=True)
    target_column = Column(String(200), nullable=False)
    strategy = Column(String(50), default="auto")
    missing_strategy = Column(String(50), default="auto")
    encoding_strategy = Column(String(50), default="auto")
    scaling_method = Column(String(50), default="standard")
    drop_threshold = Column(Float, default=0.5)
    file_path = Column(String(1000), nullable=True)
    rows_before = Column(Integer, nullable=True)
    rows_after = Column(Integer, nullable=True)
    columns_before = Column(Integer, nullable=True)
    columns_after = Column(Integer, nullable=True)
    problem_type = Column(String(50), nullable=True)
    preprocessing_report = Column(JSON, nullable=True)
    status = Column(String(50), default="pending")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    dataset = relationship("Dataset")
    version = relationship("DatasetVersion")


class EngineeredDataset(Base):
    __tablename__ = "engineered_datasets"

    id = Column(Integer, primary_key=True, index=True)
    processed_dataset_id = Column(Integer, ForeignKey("processed_datasets.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(1000), nullable=False)
    target_column = Column(String(200), nullable=False)
    fe_config = Column(Text, nullable=True)
    fe_report = Column(Text, nullable=True)
    rows = Column(Integer, nullable=True)
    columns = Column(Integer, nullable=True)
    status = Column(String(50), default="completed")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    processed_dataset = relationship("ProcessedDataset")