"""
Dataset Schemas - Pydantic models
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.datasets.models import DatasetStatus


class DatasetVersionResponse(BaseModel):
    id: int
    dataset_id: int
    version_number: int
    version_label: Optional[str]
    notes: Optional[str]
    file_size_bytes: Optional[int]
    row_count: Optional[int]
    column_count: Optional[int]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DatasetResponse(BaseModel):
    id: int
    owner_id: int
    name: str
    description: Optional[str]
    status: DatasetStatus
    original_filename: str
    file_extension: str
    file_size_bytes: Optional[int]
    row_count: Optional[int]
    column_count: Optional[int]
    column_names: Optional[List[str]]
    dtypes_info: Optional[Dict[str, str]]
    missing_values_info: Optional[Dict[str, int]]
    preview_data: Optional[List[Dict[str, Any]]]
    created_at: datetime
    updated_at: Optional[datetime]
    versions: List[DatasetVersionResponse] = []

    class Config:
        from_attributes = True


class DatasetListItem(BaseModel):
    id: int
    name: str
    description: Optional[str]
    status: DatasetStatus
    original_filename: str
    file_size_bytes: Optional[int]
    row_count: Optional[int]
    column_count: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class DatasetUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class NewVersionRequest(BaseModel):
    version_label: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=500)
