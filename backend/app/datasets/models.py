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

    # Dataset info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(DatasetStatus), default=DatasetStatus.uploading)

    # File info (of the latest/original upload)
    original_filename = Column(String(500), nullable=False)
    file_extension = Column(String(10), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=True)

    # Quick stats (populated after processing)
    row_count = Column(Integer, nullable=True)
    column_count = Column(Integer, nullable=True)
    column_names = Column(JSON, nullable=True)        # list of column names
    dtypes_info = Column(JSON, nullable=True)          # {col: dtype}
    missing_values_info = Column(JSON, nullable=True)  # {col: count}
    preview_data = Column(JSON, nullable=True)         # first 5 rows as list of dicts

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="datasets")
    versions = relationship("DatasetVersion", back_populates="dataset", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Dataset(id={self.id}, name={self.name}, owner={self.owner_id})>"


class DatasetVersion(Base):
    __tablename__ = "dataset_versions"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)

    # Version info
    version_number = Column(Integer, nullable=False, default=1)  # 1, 2, 3...
    version_label = Column(String(50), nullable=True)            # e.g. "Cleaned", "Encoded"
    notes = Column(Text, nullable=True)

    # File path on disk
    file_path = Column(String(1000), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=True)

    # Stats for this version
    row_count = Column(Integer, nullable=True)
    column_count = Column(Integer, nullable=True)

    # Whether this is the currently active version
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    dataset = relationship("Dataset", back_populates="versions")

    def __repr__(self):
        return f"<DatasetVersion(dataset={self.dataset_id}, v={self.version_number})>"
