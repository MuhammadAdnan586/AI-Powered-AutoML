"""
Data Quality API Routes
Endpoints: quality report, quality score, correlation analysis
"""
import json
import pickle
import pandas as pd
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.data_quality.analyzer import DataQualityAnalyzer
from app.auth.dependencies import get_current_user
from app.database.connection import get_db
from app.auth.models import User
from app.datasets.models import Dataset, DatasetVersion

router = APIRouter(prefix="/data-quality", tags=["Data Quality"])
UPLOADS_DIR = Path("uploads")


def load_dataset(dataset_id: int, db: Session, user: User) -> pd.DataFrame:
    """Load dataset CSV/Excel by ID using the active version's file path."""
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.owner_id == user.id
    ).first()
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")

    version = db.query(DatasetVersion).filter(
        DatasetVersion.dataset_id == dataset_id,
        DatasetVersion.is_active == True
    ).first()
    if not version:
        raise HTTPException(status_code=404, detail="No active version found for this dataset")

    if version.file_path.endswith(".csv"):
        for encoding in ["utf-8", "latin-1", "windows-1252", "utf-8-sig", "cp1252"]:
            try:
                return pd.read_csv(version.file_path, low_memory=False, encoding=encoding)
            except (UnicodeDecodeError, Exception):
                continue
        raise HTTPException(status_code=422, detail="Could not decode CSV file")
    return pd.read_excel(version.file_path)


@router.get("/report/{dataset_id}")
async def get_quality_report(
    dataset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate full data quality report for a dataset.
    Returns: score, grade, recommendations, missing values, outliers, correlations.
    """
    try:
        df = load_dataset(dataset_id, db, current_user)
        analyzer = DataQualityAnalyzer(df, dataset_id)
        report = analyzer.analyze()
        return {
            "status": "success",
            "dataset_id": dataset_id,
            "report": report
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quality analysis failed: {str(e)}")


@router.get("/score/{dataset_id}")
async def get_quality_score(
    dataset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get just the quality score and grade (fast endpoint)."""
    try:
        df = load_dataset(dataset_id, db, current_user)
        analyzer = DataQualityAnalyzer(df, dataset_id)
        report = analyzer.analyze()
        return {
            "dataset_id": dataset_id,
            "quality_score": report["quality_score"],
            "quality_grade": report["quality_grade"],
            "recommendations": report["recommendations"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/correlation/{dataset_id}")
async def get_correlation_analysis(
    dataset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get correlation matrix and highly correlated feature pairs."""
    try:
        df = load_dataset(dataset_id, db, current_user)
        analyzer = DataQualityAnalyzer(df, dataset_id)
        corr_data = analyzer._correlation_analysis()
        heatmap_path = analyzer._plot_correlation_heatmap()
        return {
            "dataset_id": dataset_id,
            "correlation": corr_data,
            "heatmap_plot": heatmap_path
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/missing/{dataset_id}")
async def get_missing_values_report(
    dataset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed missing values breakdown."""
    try:
        df = load_dataset(dataset_id, db, current_user)
        analyzer = DataQualityAnalyzer(df, dataset_id)
        missing = analyzer._check_missing()
        plot = analyzer._plot_missing_values()
        return {
            "dataset_id": dataset_id,
            "missing_values": missing,
            "missing_plot": plot
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))