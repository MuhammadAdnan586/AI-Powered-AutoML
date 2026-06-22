"""
Dataset Router
POST   /datasets/upload
GET    /datasets/
GET    /datasets/{id}
PUT    /datasets/{id}
DELETE /datasets/{id}
POST   /datasets/{id}/versions
GET    /datasets/{id}/versions
GET    /datasets/{id}/download
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path

from app.database.connection import get_db
from app.auth.models import User
from app.auth.dependencies import get_current_user
from app.datasets.service import DatasetService
from app.datasets.schemas import (
    DatasetResponse,
    DatasetListItem,
    DatasetVersionResponse,
    DatasetUpdateRequest,
)

router = APIRouter(prefix="/datasets", tags=["Datasets"])


@router.post("/upload", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: UploadFile = File(...),
    name: str = Form(..., min_length=1, max_length=255),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DatasetService.upload_dataset(db, file, name, description or "", current_user)


@router.get("/", response_model=List[DatasetListItem])
def list_datasets(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DatasetService.list_datasets(db, current_user, skip=skip, limit=limit)


# ✅ Static routes PEHLE — /{dataset_id} se pehle
@router.get("/processed")
def list_processed_datasets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all processed datasets for current user"""
    from app.datasets.models import ProcessedDataset, Dataset
    results = (
        db.query(ProcessedDataset)
        .join(Dataset, ProcessedDataset.dataset_id == Dataset.id)
        .filter(Dataset.owner_id == current_user.id)
        .order_by(ProcessedDataset.created_at.desc())
        .all()
    )
    return {
        "datasets": [
            {
                "id": r.id,
                "name": f"Processed - {r.dataset_id}",
                "rows": r.rows_after,
                "columns": r.columns_after,
                "target_column": r.target_column,
                "problem_type": r.problem_type,
                "created_at": str(r.created_at),
            }
            for r in results
        ]
    }


@router.get("/engineered")
def list_engineered_datasets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all engineered datasets for current user"""
    from app.datasets.models import EngineeredDataset, ProcessedDataset, Dataset
    results = (
        db.query(EngineeredDataset)
        .join(ProcessedDataset, EngineeredDataset.processed_dataset_id == ProcessedDataset.id)
        .join(Dataset, ProcessedDataset.dataset_id == Dataset.id)
        .filter(Dataset.owner_id == current_user.id)
        .order_by(EngineeredDataset.created_at.desc())
        .all()
    )
    return {
        "datasets": [
            {
                "id": r.id,
                "name": f"Engineered - Dataset #{r.processed_dataset.dataset_id}",
                "original_name": f"Engineered - Dataset #{r.processed_dataset.dataset_id}",
                "rows": r.rows,
                "columns": r.columns,
                "target_column": r.target_column,
                "created_at": str(r.created_at),
            }
            for r in results
        ]
    }


# ✅ Dynamic routes BAAD MEIN
@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DatasetService.get_dataset(db, dataset_id, current_user)


@router.put("/{dataset_id}", response_model=DatasetResponse)
def update_dataset(
    dataset_id: int,
    data: DatasetUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DatasetService.update_dataset(
        db, dataset_id, current_user,
        name=data.name,
        description=data.description,
    )


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    DatasetService.delete_dataset(db, dataset_id, current_user)


@router.post("/{dataset_id}/versions", response_model=DatasetVersionResponse, status_code=201)
async def create_new_version(
    dataset_id: int,
    file: UploadFile = File(...),
    version_label: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DatasetService.create_version(
        db, dataset_id, file, version_label or "", notes or "", current_user
    )


@router.get("/{dataset_id}/versions", response_model=List[DatasetVersionResponse])
def list_versions(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset = DatasetService.get_dataset(db, dataset_id, current_user)
    return dataset.versions


@router.get("/{dataset_id}/download")
def download_dataset(
    dataset_id: int,
    version: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.datasets.models import DatasetVersion

    dataset = DatasetService.get_dataset(db, dataset_id, current_user)

    if version:
        ver = db.query(DatasetVersion).filter(
            DatasetVersion.dataset_id == dataset_id,
            DatasetVersion.version_number == version,
        ).first()
    else:
        ver = db.query(DatasetVersion).filter(
            DatasetVersion.dataset_id == dataset_id,
            DatasetVersion.is_active == True,
        ).first()

    if not ver:
        raise HTTPException(status_code=404, detail="Version not found")

    file_path = Path(ver.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=str(file_path),
        filename=dataset.original_filename,
        media_type="application/octet-stream",
    )