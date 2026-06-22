"""
Module 2 - Preprocessing API Routes
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
import uuid
import logging

from .service import PreprocessingService, detect_problem_type
from ..database.connection import get_db

router = APIRouter(prefix="/preprocessing", tags=["Preprocessing"])
logger = logging.getLogger(__name__)

UPLOAD_DIR = "uploads"


class PreprocessingConfig(BaseModel):
    dataset_id: int
    target_column: str
    remove_duplicates: bool = True
    missing_strategy: str = "auto"
    encoding_strategy: str = "auto"
    scaling_method: str = "standard"
    drop_threshold: float = 0.5
    outlier_handling: str = "clip"


class ProblemTypeRequest(BaseModel):
    dataset_id: int
    target_column: str


@router.post("/analyze")
async def analyze_dataset(dataset_id: int, db: Session = Depends(get_db)):
    try:
        from ..datasets.models import Dataset
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        latest_version = dataset.versions[-1] if dataset.versions else None
        if not latest_version:
            raise HTTPException(status_code=404, detail="No file found for dataset")

        service = PreprocessingService()
        df = service.load_dataset(latest_version.file_path)
        info = service.get_dataset_info(df)

        return JSONResponse(content={"success": True, "dataset_id": dataset_id, "info": info})

    except Exception as e:
        logger.error(f"Dataset analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-problem-type")
async def detect_problem(request: ProblemTypeRequest, db: Session = Depends(get_db)):
    try:
        from ..datasets.models import Dataset
        dataset = db.query(Dataset).filter(Dataset.id == request.dataset_id).first()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        latest_version = dataset.versions[-1] if dataset.versions else None
        if not latest_version:
            raise HTTPException(status_code=404, detail="No file found")

        service = PreprocessingService()
        df = service.load_dataset(latest_version.file_path)
        result = detect_problem_type(df, request.target_column)

        return JSONResponse(content={"success": True, **result})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run")
async def run_preprocessing(config: PreprocessingConfig, db: Session = Depends(get_db)):
    try:
        from ..datasets.models import Dataset, ProcessedDataset

        dataset = db.query(Dataset).filter(Dataset.id == config.dataset_id).first()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        latest_version = dataset.versions[-1] if dataset.versions else None
        if not latest_version:
            raise HTTPException(status_code=404, detail="No file found for dataset")

        service = PreprocessingService()
        df = service.load_dataset(latest_version.file_path)

        pipeline_config = {
            'remove_duplicates': config.remove_duplicates,
            'missing_strategy': config.missing_strategy,
            'encoding_strategy': config.encoding_strategy,
            'scaling_method': config.scaling_method,
            'drop_threshold': config.drop_threshold,
            'outlier_handling': config.outlier_handling
        }

        rows_before = len(df)
        cols_before = len(df.columns)

        df_processed, report = service.full_preprocessing_pipeline(
            df,
            target_column=config.target_column,
            config=pipeline_config
        )

        os.makedirs(UPLOAD_DIR, exist_ok=True)
        processed_path = os.path.join(UPLOAD_DIR, f"processed_{uuid.uuid4().hex}.csv")
        df_processed.to_csv(processed_path, index=False)

        problem_info = detect_problem_type(df_processed, config.target_column)

        processed = ProcessedDataset(
            dataset_id=config.dataset_id,
            version_id=latest_version.id,
            target_column=config.target_column,
            strategy=config.missing_strategy,
            missing_strategy=config.missing_strategy,
            encoding_strategy=config.encoding_strategy,
            scaling_method=config.scaling_method,
            drop_threshold=config.drop_threshold,
            file_path=processed_path,
            rows_before=rows_before,
            rows_after=len(df_processed),
            columns_before=cols_before,
            columns_after=len(df_processed.columns),
            problem_type=problem_info.get('problem_type'),
            preprocessing_report=report,
            status="completed"
        )
        db.add(processed)
        db.commit()
        db.refresh(processed)

        return JSONResponse(content={
            "success": True,
            "processed_dataset_id": processed.id,
            "preprocessing_report": report,
            "problem_type": problem_info,
            "processed_shape": list(df_processed.shape)
        })

    except Exception as e:
        logger.error(f"Preprocessing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/{dataset_id}")
async def get_preprocessing_report(dataset_id: int, db: Session = Depends(get_db)):
    try:
        from ..datasets.models import ProcessedDataset

        processed = db.query(ProcessedDataset).filter(
            ProcessedDataset.dataset_id == dataset_id
        ).order_by(ProcessedDataset.created_at.desc()).first()

        if not processed:
            raise HTTPException(status_code=404, detail="No preprocessing report found")

        return JSONResponse(content={
            "success": True,
            "report": processed.preprocessing_report,
            "processed_dataset_id": processed.id
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preview/{processed_dataset_id}")
async def preview_processed_dataset(processed_dataset_id: int, rows: int = 10, db: Session = Depends(get_db)):
    """Preview the cleaned/processed dataset — should have no missing values, no duplicates."""
    try:
        from ..datasets.models import ProcessedDataset

        processed = db.query(ProcessedDataset).filter(
            ProcessedDataset.id == processed_dataset_id
        ).first()
        if not processed:
            raise HTTPException(status_code=404, detail="Processed dataset not found")

        service = PreprocessingService()
        df = service.load_dataset(processed.file_path)
        info = service.get_dataset_info(df)
        info["sample_data"] = df.head(rows).to_dict(orient="records")

        return JSONResponse(content={
            "success": True,
            "processed_dataset_id": processed_dataset_id,
            "info": info
        })

    except Exception as e:
        logger.error(f"Processed dataset preview error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))