"""
Explainability API Routes
Endpoints: SHAP values, feature importance, plots
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import pickle
import os
import json
import pandas as pd
from pathlib import Path
from sqlalchemy.orm import Session

from app.explainability.shap_service import SHAPExplainer
from app.auth.dependencies import get_current_user
from app.database.connection import get_db
from app.auth.models import User

router = APIRouter(prefix="/explainability", tags=["Explainability"])

MODELS_DIR = Path("models")
ARTIFACTS_DIR = Path("artifacts/explainability")
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


class ExplainRequest(BaseModel):
    session_id: str
    num_samples: Optional[int] = 100


def load_model_and_data(session_id: str, db: Session):
    """Load trained model and data using session JSON format."""

    # Load session JSON
    session_file = MODELS_DIR / f"session_{session_id}.json"
    if not session_file.exists():
        raise HTTPException(status_code=404, detail=f"Trained model not found for session '{session_id}'")

    with open(session_file) as f:
        session_data = json.load(f)

    best_model_name = session_data.get("best_model", "")
    short_id = session_id[:8]

    # Find model file
    model_filename = f"{best_model_name.replace(' ', '_')}_{short_id}.pkl"
    model_path = MODELS_DIR / model_filename
    if not model_path.exists():
        matches = list(MODELS_DIR.glob(f"*_{short_id}.pkl"))
        if not matches:
            raise HTTPException(status_code=404, detail=f"Model file not found: {model_filename}")
        model_path = matches[0]

    try:
        import joblib
        model = joblib.load(model_path)
    except Exception:
        with open(model_path, "rb") as f:
            model = pickle.load(f)

    model_name = best_model_name

    # Load engineered dataset
    engineered_dataset_path = session_data.get("engineered_file_path")

    if engineered_dataset_path and Path(engineered_dataset_path).exists():
        df = pd.read_csv(engineered_dataset_path)
    else:
        upload_dir = Path("uploads")
        eng_files = sorted(
            upload_dir.glob("engineered_*.csv"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        if not eng_files:
            raise HTTPException(status_code=404, detail="Engineered dataset not found")
        df = pd.read_csv(eng_files[0])

    target_column = session_data.get("target_column", "")

    # Prefer the exact feature columns saved during training (matches the
    # model''s expected input shape, e.g. excludes identifier columns like ''id'').
    saved_feature_columns = None
    best_model_file = MODELS_DIR / f"{session_id}_best_model.pkl"
    try:
        with open(best_model_file, "rb") as f:
            saved_obj = pickle.load(f)
        if isinstance(saved_obj, dict) and "feature_columns" in saved_obj:
            saved_feature_columns = saved_obj["feature_columns"]
            model = saved_obj["model"]
    except Exception:
        pass

    if saved_feature_columns:
        for col in saved_feature_columns:
            if col not in df.columns:
                df[col] = 0
        X = df[saved_feature_columns]
    else:
        feature_columns = [c for c in df.columns if c != target_column]
        X = df[feature_columns].select_dtypes(include=["number"])

    return model, X, model_name


@router.post("/explain")
async def explain_model(
    request: ExplainRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate full SHAP explanation for a trained model."""
    try:
        model, X, model_name = load_model_and_data(request.session_id, db)
        explainer = SHAPExplainer(model, X)
        effective_samples = request.num_samples
        if type(explainer.explainer).__name__ == "KernelExplainer":
            effective_samples = min(request.num_samples, 25)
        X_sample = X.sample(min(effective_samples, len(X)), random_state=42)
        result = explainer.get_full_explanation(X_sample, request.session_id)
        return {
            "status": "success",
            "session_id": request.session_id,
            "model_name": model_name,
            "explanation": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")


@router.post("/feature-importance")
async def get_feature_importance(
    request: ExplainRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get ranked feature importance using SHAP values."""
    try:
        model, X, model_name = load_model_and_data(request.session_id, db)
        explainer = SHAPExplainer(model, X)
        effective_samples = request.num_samples
        if type(explainer.explainer).__name__ == "KernelExplainer":
            effective_samples = min(request.num_samples, 25)
        X_sample = X.sample(min(effective_samples, len(X)), random_state=42)
        importance = explainer.get_feature_importance(X_sample)
        return {
            "status": "success",
            "model_name": model_name,
            "feature_importance": importance
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plots/{session_id}")
async def get_explanation_plots(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get list of available explanation plots for a session."""
    plots = {}
    for plot_type in ["shap_summary", "waterfall", "force"]:
        path = ARTIFACTS_DIR / f"{plot_type}_{session_id}.png"
        if path.exists():
            plots[plot_type] = str(path)
    return {"session_id": session_id, "plots": plots}
