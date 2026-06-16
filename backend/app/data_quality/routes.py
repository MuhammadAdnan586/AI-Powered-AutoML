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

from app.data_quality.analyzer import DataQualityAnalyzer
from app.auth.dependencies import get_current_user
from app.database.connection import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/data-quality", tags=["Data Quality"])

UPLOADS_DIR = Path("uploads")


def load_dataset(dataset_id: int) -> pd.DataFrame:
    """Load dataset CSV/Excel by ID."""
    for ext in [".csv", ".xlsx", ".xls"]:
        path = UPLOADS_DIR / f"dataset_{dataset_id}{ext}"
        if path.exists():
            return pd.read_csv(path) if ext == ".csv" else pd.read_excel(path)
    raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")


@router.get("/report/{dataset_id}")
async def get_quality_report(
    dataset_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate full data quality report for a dataset.
    Returns: score, grade, recommendations, missing values, outliers, correlations.
    """
    try:
        df = load_dataset(dataset_id)
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
    current_user=Depends(get_current_user)
):
    """Get just the quality score and grade (fast endpoint)."""
    try:
        df = load_dataset(dataset_id)
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
    current_user=Depends(get_current_user)
):
    """Get correlation matrix and highly correlated feature pairs."""
    try:
        df = load_dataset(dataset_id)
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
    current_user=Depends(get_current_user)
):
    """Get detailed missing values breakdown."""
    try:
        df = load_dataset(dataset_id)
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
