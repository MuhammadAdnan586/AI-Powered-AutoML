"""
Module 2 - Preprocessing API Routes
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import pandas as pd
import os
import uuid
import logging

from .service import PreprocessingService, detect_problem_type
from ..database.connection import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/preprocessing", tags=["Preprocessing"])
logger = logging.getLogger(__name__)

UPLOAD_DIR = "uploads"


class PreprocessingConfig(BaseModel):
    dataset_id: int
    target_column: str
    remove_duplicates: bool = True
    missing_strategy: str = "auto"  # auto, drop, impute
    encoding_strategy: str = "auto"  # auto, label, onehot
    scaling_method: str = "standard"  # standard, minmax, none
    drop_threshold: float = 0.5


class ProblemTypeRequest(BaseModel):
    dataset_id: int
    target_column: str


@router.post("/analyze")
async def analyze_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Analyze dataset and return comprehensive info."""
    try:
        # Get dataset from DB
        from ..datasets.models import Dataset
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        service = PreprocessingService()
        df = service.load_dataset(dataset.file_path)
        info = service.get_dataset_info(df)
        
        return JSONResponse(content={
            "success": True,
            "dataset_id": dataset_id,
            "info": info
        })
    
    except Exception as e:
        logger.error(f"Dataset analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-problem-type")
async def detect_problem(request: ProblemTypeRequest, db: Session = Depends(get_db)):
    """Auto-detect if problem is Classification or Regression."""
    try:
        from ..datasets.models import Dataset
        dataset = db.query(Dataset).filter(Dataset.id == request.dataset_id).first()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        service = PreprocessingService()
        df = service.load_dataset(dataset.file_path)
        result = detect_problem_type(df, request.target_column)
        
        return JSONResponse(content={
            "success": True,
            **result
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run")
async def run_preprocessing(config: PreprocessingConfig, db: Session = Depends(get_db)):
    """Run complete preprocessing pipeline on a dataset."""
    try:
        from ..datasets.models import Dataset, ProcessedDataset
        
        dataset = db.query(Dataset).filter(Dataset.id == config.dataset_id).first()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        service = PreprocessingService()
        df = service.load_dataset(dataset.file_path)
        
        pipeline_config = {
            'remove_duplicates': config.remove_duplicates,
            'missing_strategy': config.missing_strategy,
            'encoding_strategy': config.encoding_strategy,
            'scaling_method': config.scaling_method,
            'drop_threshold': config.drop_threshold
        }
        
        df_processed, report = service.full_preprocessing_pipeline(
            df, 
            target_column=config.target_column,
            config=pipeline_config
        )
        
        # Save processed dataset
        processed_path = os.path.join(UPLOAD_DIR, f"processed_{uuid.uuid4().hex}.csv")
        df_processed.to_csv(processed_path, index=False)
        
        # Save to DB
        processed = ProcessedDataset(
            original_dataset_id=config.dataset_id,
            file_path=processed_path,
            target_column=config.target_column,
            preprocessing_config=str(pipeline_config),
            preprocessing_report=str(report),
            rows=len(df_processed),
            columns=len(df_processed.columns)
        )
        db.add(processed)
        db.commit()
        db.refresh(processed)
        
        # Detect problem type
        problem_info = detect_problem_type(df_processed, config.target_column)
        
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
    """Get preprocessing report for a dataset."""
    try:
        from ..datasets.models import ProcessedDataset
        
        processed = db.query(ProcessedDataset).filter(
            ProcessedDataset.original_dataset_id == dataset_id
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
