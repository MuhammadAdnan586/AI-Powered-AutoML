"""
Module 2 - Feature Engineering API Routes
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import logging

from .service import FeatureEngineeringService
from ..database.connection import get_db

router = APIRouter(prefix="/feature-engineering", tags=["Feature Engineering"])
logger = logging.getLogger(__name__)


class FeatureEngineeringConfig(BaseModel):
    processed_dataset_id: int
    target_column: str
    problem_type: str = "regression"
    auto_generate: bool = False
    remove_low_variance: bool = False
    remove_correlated: bool = False
    select_best: bool = False
    k_best: int = 50
    variance_threshold: float = 0.01
    correlation_threshold: float = 0.95


@router.post("/run")
async def run_feature_engineering(config: FeatureEngineeringConfig, db: Session = Depends(get_db)):
    """Run complete feature engineering pipeline."""
    try:
        import pandas as pd
        import os
        import uuid
        from ..datasets.models import ProcessedDataset, EngineeredDataset

        processed = db.query(ProcessedDataset).filter(
            ProcessedDataset.id == config.processed_dataset_id
        ).first()
        
        if not processed:
            raise HTTPException(status_code=404, detail="Processed dataset not found")
        
        df = pd.read_csv(processed.file_path)
        
        service = FeatureEngineeringService()
        pipeline_config = {
            'auto_generate': config.auto_generate,
            'remove_low_variance': config.remove_low_variance,
            'remove_correlated': config.remove_correlated,
            'select_best': config.select_best,
            'k_best': config.k_best,
            'variance_threshold': config.variance_threshold,
            'correlation_threshold': config.correlation_threshold
        }
        
        df_engineered, report = service.full_feature_engineering_pipeline(
            df, 
            target_column=config.target_column,
            problem_type=config.problem_type,
            config=pipeline_config
        )
        
        # Save engineered dataset
        output_path = f"uploads/engineered_{uuid.uuid4().hex}.csv"
        df_engineered.to_csv(output_path, index=False)
        
        # Save to DB
        engineered = EngineeredDataset(
            processed_dataset_id=config.processed_dataset_id,
            file_path=output_path,
            target_column=config.target_column,
            fe_config=str(pipeline_config),
            fe_report=str(report),
            rows=len(df_engineered),
            columns=len(df_engineered.columns)
        )
        db.add(engineered)
        db.commit()
        db.refresh(engineered)
        
        return JSONResponse(content={
            "success": True,
            "engineered_dataset_id": engineered.id,
            "feature_engineering_report": report,
            "final_shape": list(df_engineered.shape),
            "final_columns": list(df_engineered.columns)
        })
    
    except Exception as e:
        logger.error(f"Feature engineering error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/correlation/{dataset_id}")
async def get_correlation_matrix(dataset_id: int, db: Session = Depends(get_db)):
    """Get correlation matrix for a dataset."""
    try:
        import pandas as pd
        from ..datasets.models import ProcessedDataset
        
        processed = db.query(ProcessedDataset).filter(
            ProcessedDataset.id == dataset_id
        ).first()
        
        if not processed:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        df = pd.read_csv(processed.file_path)
        numeric_df = df.select_dtypes(include=['number'])
        
        corr = numeric_df.corr().round(3)
        
        return JSONResponse(content={
            "success": True,
            "columns": list(corr.columns),
            "matrix": corr.values.tolist()
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/preview/{engineered_dataset_id}")
async def preview_engineered_dataset(engineered_dataset_id: int, rows: int = 10, db: Session = Depends(get_db)):
    """Preview the final feature-engineered dataset — fully numeric, ready for training."""
    try:
        import pandas as pd
        from ..datasets.models import EngineeredDataset

        engineered = db.query(EngineeredDataset).filter(
            EngineeredDataset.id == engineered_dataset_id
        ).first()
        if not engineered:
            raise HTTPException(status_code=404, detail="Engineered dataset not found")

        df = pd.read_csv(engineered.file_path)
        info = {
            "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "missing_values": {col: int(df[col].isnull().sum()) for col in df.columns},
            "duplicate_rows": int(df.duplicated().sum()),
            "numeric_columns": list(df.select_dtypes(include=["number"]).columns),
            "categorical_columns": list(df.select_dtypes(include=["object", "category"]).columns),
            "sample_data": df.head(rows).to_dict(orient="records"),
        }

        return JSONResponse(content={
            "success": True,
            "engineered_dataset_id": engineered_dataset_id,
            "info": info
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
