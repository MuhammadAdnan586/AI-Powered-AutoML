"""
Module 2 - MLflow Tracking API Routes
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from .service import MLflowTracker
import logging

router = APIRouter(prefix="/api/mlflow", tags=["MLflow Tracking"])
logger = logging.getLogger(__name__)


@router.get("/experiments")
async def get_experiments():
    """Get all MLflow experiments."""
    try:
        tracker = MLflowTracker()
        experiments = tracker.get_experiments()
        return JSONResponse(content={"success": True, "experiments": experiments})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/runs")
async def get_runs(experiment_name: str = "AutoML_Experiment"):
    """Get all runs for an experiment."""
    try:
        tracker = MLflowTracker(experiment_name)
        runs = tracker.get_runs(experiment_name)
        return JSONResponse(content={"success": True, "runs": runs})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
