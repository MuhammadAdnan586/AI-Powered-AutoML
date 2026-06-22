"""
Dataset Service - Business Logic
File upload, processing, versioning
"""
import os
import shutil
import uuid
import pandas as pd
from pathlib import Path
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.datasets.models import Dataset, DatasetVersion, DatasetStatus
from app.auth.models import User
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

UPLOAD_BASE = Path(settings.UPLOAD_DIR)
UPLOAD_BASE.mkdir(parents=True, exist_ok=True)


def get_user_upload_dir(user_id: int) -> Path:
    """Each user gets their own upload folder"""
    path = UPLOAD_BASE / str(user_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def validate_file(file: UploadFile) -> str:
    """Validate file extension and size. Returns extension."""
    filename = file.filename or ""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=400,
            detail=f"File type '.{ext}' not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}",
        )
    return ext


def read_dataframe(file_path: Path, ext: str) -> pd.DataFrame:
    """Read CSV or Excel into a DataFrame — auto-detects encoding"""
    try:
        if ext == "csv":
            for encoding in ["utf-8", "latin-1", "windows-1252", "utf-8-sig", "cp1252"]:
                try:
                    return pd.read_csv(file_path, low_memory=False, encoding=encoding)
                except (UnicodeDecodeError, Exception):
                    continue
            raise ValueError("Could not decode CSV with any known encoding")
        elif ext in ("xlsx", "xls"):
            return pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported extension: {ext}")
    except Exception as e:
        logger.error(f"Failed to read file {file_path}: {e}")
        raise HTTPException(status_code=422, detail=f"Could not parse file: {str(e)}")


def extract_stats(df: pd.DataFrame) -> dict:
    """Extract metadata statistics from a DataFrame"""
    missing = {col: int(df[col].isna().sum()) for col in df.columns}
    dtypes = {col: str(df[col].dtype) for col in df.columns}
    preview = df.head(5).where(pd.notnull(df), None).to_dict(orient="records")

    return {
        "row_count": len(df),
        "column_count": len(df.columns),
        "column_names": list(df.columns),
        "dtypes_info": dtypes,
        "missing_values_info": missing,
        "preview_data": preview,
    }


class DatasetService:

    @staticmethod
    def upload_dataset(
        db: Session,
        file: UploadFile,
        name: str,
        description: str,
        user: User,
    ) -> Dataset:
        """
        Upload and process a dataset file.
        Creates Dataset + DatasetVersion v1.
        """
        ext = validate_file(file)

        # Save file to disk
        user_dir = get_user_upload_dir(user.id)
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        file_path = user_dir / unique_name

        try:
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"File save failed: {e}")

        file_size = file_path.stat().st_size

        # Check size limit
        if file_size > settings.max_upload_size_bytes:
            file_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max: {settings.MAX_UPLOAD_SIZE_MB}MB",
            )

        # Create dataset record
        dataset = Dataset(
            owner_id=user.id,
            name=name.strip(),
            description=description.strip() if description else None,
            original_filename=file.filename,
            file_extension=ext,
            file_size_bytes=file_size,
            status=DatasetStatus.processing,
        )
        db.add(dataset)
        db.flush()

        # Process file - extract stats
        try:
            df = read_dataframe(file_path, ext)
            stats = extract_stats(df)
            dataset.row_count = stats["row_count"]
            dataset.column_count = stats["column_count"]
            dataset.column_names = stats["column_names"]
            dataset.dtypes_info = stats["dtypes_info"]
            dataset.missing_values_info = stats["missing_values_info"]
            dataset.preview_data = stats["preview_data"]
            dataset.status = DatasetStatus.ready
        except Exception as e:
            dataset.status = DatasetStatus.error
            logger.error(f"Dataset processing error: {e}")

        # Create version v1
        version = DatasetVersion(
            dataset_id=dataset.id,
            version_number=1,
            version_label="Original Upload",
            file_path=str(file_path),
            file_size_bytes=file_size,
            row_count=dataset.row_count,
            column_count=dataset.column_count,
            is_active=True,
        )
        db.add(version)
        db.commit()
        db.refresh(dataset)

        logger.info(f"Dataset uploaded: {dataset.name} (id={dataset.id}) by user {user.id}")
        return dataset

    @staticmethod
    def get_dataset(db: Session, dataset_id: int, user: User) -> Dataset:
        """Get a dataset, verifying ownership"""
        dataset = db.query(Dataset).filter(
            Dataset.id == dataset_id,
            Dataset.owner_id == user.id,
        ).first()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        return dataset

    @staticmethod
    def list_datasets(db: Session, user: User, skip: int = 0, limit: int = 20):
        """List all datasets for the current user"""
        return (
            db.query(Dataset)
            .filter(Dataset.owner_id == user.id)
            .order_by(Dataset.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update_dataset(db: Session, dataset_id: int, user: User, **kwargs) -> Dataset:
        """Update dataset metadata"""
        dataset = DatasetService.get_dataset(db, dataset_id, user)
        for key, value in kwargs.items():
            if value is not None:
                setattr(dataset, key, value)
        db.commit()
        db.refresh(dataset)
        return dataset

    @staticmethod
    def delete_dataset(db: Session, dataset_id: int, user: User) -> None:
        """Delete dataset and all its files"""
        from app.datasets.models import ProcessedDataset, EngineeredDataset

        dataset = DatasetService.get_dataset(db, dataset_id, user)

        # Step 1: Get all version IDs
        version_ids = [v.id for v in dataset.versions]

        # Step 2: Get all processed dataset IDs for this dataset
        processed_list = db.query(ProcessedDataset).filter(
            ProcessedDataset.dataset_id == dataset_id
        ).all()
        processed_ids = [r.id for r in processed_list]

        # Step 3: Delete engineered datasets
        if processed_ids:
            db.query(EngineeredDataset).filter(
                EngineeredDataset.processed_dataset_id.in_(processed_ids)
            ).delete(synchronize_session=False)

        # Step 4: Null out version_id FK to break constraint
        if version_ids:
            db.query(ProcessedDataset).filter(
                ProcessedDataset.version_id.in_(version_ids)
            ).update({"version_id": None}, synchronize_session=False)

        # Step 5: Delete processed datasets
        db.query(ProcessedDataset).filter(
            ProcessedDataset.dataset_id == dataset_id
        ).delete(synchronize_session=False)

        # Step 6: Delete version files from disk
        for version in dataset.versions:
            path = Path(version.file_path)
            if path.exists():
                path.unlink()
                logger.info(f"Deleted file: {path}")

        # Step 7: Delete dataset record (versions cascade)
        db.delete(dataset)
        db.commit()
        logger.info(f"Dataset {dataset_id} deleted by user {user.id}")

    @staticmethod
    def create_version(
        db: Session,
        dataset_id: int,
        file: UploadFile,
        label: str,
        notes: str,
        user: User,
    ) -> DatasetVersion:
        """
        Upload a new version of an existing dataset.
        Deactivates the previous active version.
        """
        dataset = DatasetService.get_dataset(db, dataset_id, user)
        ext = validate_file(file)

        # Deactivate current active version
        db.query(DatasetVersion).filter(
            DatasetVersion.dataset_id == dataset_id,
            DatasetVersion.is_active == True,
        ).update({"is_active": False})

        # Determine next version number
        latest = (
            db.query(DatasetVersion)
            .filter(DatasetVersion.dataset_id == dataset_id)
            .order_by(DatasetVersion.version_number.desc())
            .first()
        )
        next_version = (latest.version_number + 1) if latest else 1

        # Save file
        user_dir = get_user_upload_dir(user.id)
        unique_name = f"{uuid.uuid4().hex}_v{next_version}.{ext}"
        file_path = user_dir / unique_name

        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        file_size = file_path.stat().st_size

        # Process stats
        df = read_dataframe(file_path, ext)
        stats = extract_stats(df)

        # Update parent dataset quick stats
        dataset.row_count = stats["row_count"]
        dataset.column_count = stats["column_count"]
        dataset.column_names = stats["column_names"]
        dataset.dtypes_info = stats["dtypes_info"]
        dataset.missing_values_info = stats["missing_values_info"]
        dataset.preview_data = stats["preview_data"]
        dataset.status = DatasetStatus.ready

        version = DatasetVersion(
            dataset_id=dataset.id,
            version_number=next_version,
            version_label=label or f"Version {next_version}",
            notes=notes,
            file_path=str(file_path),
            file_size_bytes=file_size,
            row_count=stats["row_count"],
            column_count=stats["column_count"],
            is_active=True,
        )
        db.add(version)
        db.commit()
        db.refresh(version)

        logger.info(f"New version v{next_version} created for dataset {dataset_id}")
        return version