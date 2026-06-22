"""
Explainability API Routes
Endpoints: SHAP values, feature importance, plots
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import pickle
import pandas as pd
from pathlib import Path

from app.explainability.shap_service import SHAPExplainer
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/explainability", tags=["Explainability"])

MODELS_DIR = Path("models")
ARTIFACTS_DIR = Path("artifacts/explainability")
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


class ExplainRequest(BaseModel):
    dataset_id: int
    model_name: str
    num_samples: Optional[int] = 100


def load_model_and_data(dataset_id: int, model_name: str):
    """Load trained model and training data."""
    model_path = MODELS_DIR / f"dataset_{dataset_id}" / f"{model_name}.pkl"
    data_path = MODELS_DIR / f"dataset_{dataset_id}" / "X_train.pkl"

    if not model_path.exists():
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
    if not data_path.exists():
        raise HTTPException(status_code=404, detail="Training data not found for this dataset")

    with open(model_path, "rb") as f:
        model = pickle.load(f)
    with open(data_path, "rb") as f:
        X_train = pickle.load(f)

    return model, X_train


@router.post("/explain")
async def explain_model(
    request: ExplainRequest,
    current_user=Depends(get_current_user)
):
    """
    Generate full SHAP explanation for a trained model.
    Returns feature importance, summary plot, waterfall plot.
    """
    try:
        model, X_train = load_model_and_data(request.dataset_id, request.model_name)
        X_sample = X_train.sample(min(request.num_samples, len(X_train)), random_state=42)

        explainer = SHAPExplainer(model, X_train)
        result = explainer.get_full_explanation(X_sample, request.dataset_id)

        return {
            "status": "success",
            "dataset_id": request.dataset_id,
            "model_name": request.model_name,
            "explanation": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")


@router.post("/feature-importance")
async def get_feature_importance(
    request: ExplainRequest,
    current_user=Depends(get_current_user)
):
    """Get ranked feature importance using SHAP values."""
    try:
        model, X_train = load_model_and_data(request.dataset_id, request.model_name)
        X_sample = X_train.sample(min(request.num_samples, len(X_train)), random_state=42)

        explainer = SHAPExplainer(model, X_train)
        importance = explainer.get_feature_importance(X_sample)

        return {
            "status": "success",
            "model_name": request.model_name,
            "feature_importance": importance
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plots/{dataset_id}/{model_name}")
async def get_explanation_plots(
    dataset_id: int,
    model_name: str,
    current_user=Depends(get_current_user)
):
    """Get list of available explanation plots for a model."""
    plot_dir = ARTIFACTS_DIR
    plots = {}
    for plot_type in ["shap_summary", "waterfall", "force"]:
        path = plot_dir / f"{plot_type}_{dataset_id}.png"
        if path.exists():
            plots[plot_type] = str(path)

    return {"dataset_id": dataset_id, "model_name": model_name, "plots": plots}
