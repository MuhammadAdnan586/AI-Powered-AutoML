"""
Dashboard API Routes
Endpoints: full dashboard data, individual charts
"""
import json
import pandas as pd
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends

from app.dashboard.chart_service import DashboardChartService
from app.data_quality.analyzer import DataQualityAnalyzer
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

UPLOADS_DIR = Path("uploads")
MODELS_DIR = Path("models")


def load_dataset(dataset_id: int) -> pd.DataFrame:
    for ext in [".csv", ".xlsx"]:
        path = UPLOADS_DIR / f"dataset_{dataset_id}{ext}"
        if path.exists():
            return pd.read_csv(path) if ext == ".csv" else pd.read_excel(path)
    raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")


def load_benchmark(dataset_id: int) -> dict:
    path = MODELS_DIR / f"dataset_{dataset_id}" / "benchmark_results.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {"models": [], "best_model": {}}


def load_feature_importance(dataset_id: int) -> list:
    path = Path("artifacts/explainability") / f"feature_importance_{dataset_id}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return []


@router.get("/data/{dataset_id}")
async def get_dashboard_data(
    dataset_id: int,
    current_user=Depends(get_current_user)
):
    """
    Get all dashboard chart data for a dataset.
    Returns benchmark, quality, distributions, feature importance.
    """
    try:
        df = load_dataset(dataset_id)
        quality_report = DataQualityAnalyzer(df, dataset_id).analyze()
        benchmark = load_benchmark(dataset_id)
        feature_importance = load_feature_importance(dataset_id)

        service = DashboardChartService(dataset_id)
        charts = service.get_full_dashboard_data(
            df=df,
            quality_report=quality_report,
            benchmark_results=benchmark,
            feature_importance=feature_importance if feature_importance else None
        )

        return {"status": "success", "dataset_id": dataset_id, "charts": charts}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmark-chart/{dataset_id}")
async def get_benchmark_chart(
    dataset_id: int,
    current_user=Depends(get_current_user)
):
    """Get benchmark leaderboard chart data."""
    benchmark = load_benchmark(dataset_id)
    service = DashboardChartService(dataset_id)
    return service.get_benchmark_chart_data(benchmark)


@router.get("/quality-score/{dataset_id}")
async def get_quality_gauge(
    dataset_id: int,
    current_user=Depends(get_current_user)
):
    """Get quality score gauge data."""
    df = load_dataset(dataset_id)
    report = DataQualityAnalyzer(df, dataset_id).analyze()
    service = DashboardChartService(dataset_id)
    return service.get_quality_score_gauge(
        report["quality_score"],
        report["quality_grade"]
    )
