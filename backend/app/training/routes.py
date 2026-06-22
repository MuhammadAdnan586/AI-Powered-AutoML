from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
import os
import uuid
import logging

from ..database.connection import get_db

router = APIRouter(prefix="/training", tags=["Training"])
logger = logging.getLogger(__name__)


class TrainingConfig(BaseModel):
    engineered_dataset_id: int
    target_column: str
    problem_type: str = "regression"
    test_size: float = 0.2
    random_state: int = 42


@router.get("/status")
def training_status():
    return {"status": "Training module ready"}


@router.post("/run")
async def run_training(config: TrainingConfig, db: Session = Depends(get_db)):
    """Train multiple models and return leaderboard."""
    try:
        from ..datasets.models import EngineeredDataset
        from sklearn.model_selection import train_test_split
        from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor, GradientBoostingClassifier
        from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge
        from sklearn.metrics import (r2_score, mean_absolute_error, mean_squared_error,
                                     accuracy_score, f1_score, roc_auc_score)
        import joblib

        engineered = db.query(EngineeredDataset).filter(
            EngineeredDataset.id == config.engineered_dataset_id
        ).first()

        if not engineered:
            raise HTTPException(status_code=404, detail="Engineered dataset not found")

        df = pd.read_csv(engineered.file_path)

        if config.target_column not in df.columns:
            raise HTTPException(status_code=400, detail=f"Target column '{config.target_column}' not found")

        X = df.drop(columns=[config.target_column])
        y = df[config.target_column]

        # Keep only numeric columns
        X = X.select_dtypes(include=[np.number])

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=config.test_size, random_state=config.random_state
        )

        leaderboard = []

        if config.problem_type == "regression":
            models = {
                "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
                "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
                "Ridge Regression": Ridge(),
                "Linear Regression": LinearRegression(),
            }

            for name, model in models.items():
                try:
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                    r2 = round(float(r2_score(y_test, y_pred)), 4)
                    mae = round(float(mean_absolute_error(y_test, y_pred)), 2)
                    rmse = round(float(np.sqrt(mean_squared_error(y_test, y_pred))), 2)

                    # Save model
                    os.makedirs("models", exist_ok=True)
                    model_path = f"models/{name.replace(' ', '_')}_{uuid.uuid4().hex[:8]}.pkl"
                    joblib.dump(model, model_path)

                    leaderboard.append({
                        "model": name,
                        "r2_score": r2,
                        "mae": mae,
                        "rmse": rmse,
                        "model_path": model_path
                    })
                except Exception as e:
                    logger.error(f"Model {name} failed: {str(e)}")

            leaderboard.sort(key=lambda x: x["r2_score"], reverse=True)

        else:  # classification
            models = {
                "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
                "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, random_state=42),
                "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
            }

            for name, model in models.items():
                try:
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                    acc = round(float(accuracy_score(y_test, y_pred)), 4)
                    f1 = round(float(f1_score(y_test, y_pred, average='weighted')), 4)

                    os.makedirs("models", exist_ok=True)
                    model_path = f"models/{name.replace(' ', '_')}_{uuid.uuid4().hex[:8]}.pkl"
                    joblib.dump(model, model_path)

                    leaderboard.append({
                        "model": name,
                        "accuracy": acc,
                        "f1_score": f1,
                        "model_path": model_path
                    })
                except Exception as e:
                    logger.error(f"Model {name} failed: {str(e)}")

            leaderboard.sort(key=lambda x: x["accuracy"], reverse=True)

        best_model = leaderboard[0] if leaderboard else None

        return JSONResponse(content={
            "success": True,
            "problem_type": config.problem_type,
            "leaderboard": leaderboard,
            "best_model": best_model,
            "training_shape": list(X_train.shape),
            "test_shape": list(X_test.shape)
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Training error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))