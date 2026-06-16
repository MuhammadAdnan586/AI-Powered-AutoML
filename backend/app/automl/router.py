"""
Module 2 - AutoML API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import logging
import uuid
import json
import pandas as pd

from .service import AutoMLService
from ..database.connection import get_db

router = APIRouter(prefix="/api/automl", tags=["AutoML"])
logger = logging.getLogger(__name__)

# In-memory session store (use Redis in production)
training_sessions: Dict[str, Dict] = {}


class AutoMLRequest(BaseModel):
    engineered_dataset_id: int
    target_column: str
    problem_type: str  # 'classification' or 'regression'
    test_size: float = 0.2
    models_to_train: Optional[List[str]] = None  # None = train all recommended
    hyperparameter_tuning: bool = False


class ModelPredictRequest(BaseModel):
    session_id: str
    model_name: str
    data: Dict[str, Any]  # {feature: value, ...}


@router.post("/train")
async def start_training(
    request: AutoMLRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start AutoML training — runs in background."""
    
    session_id = str(uuid.uuid4())
    training_sessions[session_id] = {
        "status": "starting",
        "progress": 0,
        "dataset_id": request.engineered_dataset_id
    }
    
    background_tasks.add_task(
        _run_training_task,
        session_id=session_id,
        request=request,
        db=db
    )
    
    return JSONResponse(content={
        "success": True,
        "session_id": session_id,
        "message": "Training started in background",
        "status_url": f"/api/automl/status/{session_id}"
    })


async def _run_training_task(session_id: str, request: AutoMLRequest, db: Session):
    """Background training task."""
    try:
        from ..datasets.models import EngineeredDataset, TrainingSession
        
        training_sessions[session_id]["status"] = "loading_data"
        
        dataset = db.query(EngineeredDataset).filter(
            EngineeredDataset.id == request.engineered_dataset_id
        ).first()
        
        if not dataset:
            training_sessions[session_id]["status"] = "failed"
            training_sessions[session_id]["error"] = "Dataset not found"
            return
        
        df = pd.read_csv(dataset.file_path)
        
        training_sessions[session_id]["status"] = "training"
        training_sessions[session_id]["progress"] = 10
        
        service = AutoMLService()
        results = service.run_automl(
            df=df,
            target_column=request.target_column,
            problem_type=request.problem_type,
            test_size=request.test_size,
            models_to_train=request.models_to_train,
            hyperparameter_tuning=request.hyperparameter_tuning,
            session_id=session_id
        )
        
        training_sessions[session_id]["status"] = "saving"
        
        # Save session to DB
        session_record = TrainingSession(
            session_id=session_id,
            dataset_id=request.engineered_dataset_id,
            target_column=request.target_column,
            problem_type=request.problem_type,
            best_model=results.get('best_model'),
            best_score=float(results.get('best_score', 0)),
            results=json.dumps(results),
            status="completed"
        )
        db.add(session_record)
        db.commit()
        
        training_sessions[session_id]["status"] = "completed"
        training_sessions[session_id]["progress"] = 100
        training_sessions[session_id]["results"] = results
        training_sessions[session_id]["db_id"] = session_record.id
        
        logger.info(f"Training session {session_id} completed. Best model: {results.get('best_model')}")
    
    except Exception as e:
        logger.error(f"Training failed for session {session_id}: {str(e)}")
        training_sessions[session_id]["status"] = "failed"
        training_sessions[session_id]["error"] = str(e)


@router.get("/status/{session_id}")
async def get_training_status(session_id: str):
    """Get training status and progress."""
    if session_id not in training_sessions:
        raise HTTPException(status_code=404, detail="Training session not found")
    
    session = training_sessions[session_id]
    
    response = {
        "session_id": session_id,
        "status": session.get("status"),
        "progress": session.get("progress", 0)
    }
    
    if session.get("status") == "completed":
        response["results"] = session.get("results")
    elif session.get("status") == "failed":
        response["error"] = session.get("error")
    
    return JSONResponse(content=response)


@router.get("/leaderboard/{session_id}")
async def get_leaderboard(session_id: str, db: Session = Depends(get_db)):
    """Get model comparison leaderboard for a training session."""
    
    # Check in-memory first
    if session_id in training_sessions and training_sessions[session_id].get("status") == "completed":
        results = training_sessions[session_id].get("results", {})
        return JSONResponse(content={
            "success": True,
            "session_id": session_id,
            "leaderboard": results.get("leaderboard", []),
            "best_model": results.get("best_model"),
            "best_score": results.get("best_score"),
            "problem_type": results.get("problem_type")
        })
    
    # Fall back to DB
    from ..datasets.models import TrainingSession
    session_record = db.query(TrainingSession).filter(
        TrainingSession.session_id == session_id
    ).first()
    
    if not session_record:
        raise HTTPException(status_code=404, detail="Session not found")
    
    results = json.loads(session_record.results)
    
    return JSONResponse(content={
        "success": True,
        "session_id": session_id,
        "leaderboard": results.get("leaderboard", []),
        "best_model": results.get("best_model"),
        "best_score": results.get("best_score"),
        "problem_type": results.get("problem_type")
    })


@router.get("/sessions")
async def list_sessions(db: Session = Depends(get_db)):
    """List all training sessions."""
    from ..datasets.models import TrainingSession
    
    sessions = db.query(TrainingSession).order_by(
        TrainingSession.created_at.desc()
    ).limit(20).all()
    
    return JSONResponse(content={
        "success": True,
        "sessions": [
            {
                "id": s.id,
                "session_id": s.session_id,
                "dataset_id": s.dataset_id,
                "target_column": s.target_column,
                "problem_type": s.problem_type,
                "best_model": s.best_model,
                "best_score": s.best_score,
                "status": s.status,
                "created_at": str(s.created_at)
            }
            for s in sessions
        ]
    })


@router.get("/models")
async def list_available_models(problem_type: str = "classification"):
    """List all available models for AutoML."""
    from .service import CLASSIFICATION_MODELS, REGRESSION_MODELS
    
    registry = CLASSIFICATION_MODELS if problem_type == "classification" else REGRESSION_MODELS
    
    models = [
        {
            "model_name": key,
            "display_name": val["display_name"],
            "category": val["category"],
            "supports_tuning": bool(val.get("param_grid"))
        }
        for key, val in registry.items()
    ]
    
    return JSONResponse(content={
        "success": True,
        "problem_type": problem_type,
        "models": models
    })


@router.post("/predict/{session_id}")
async def predict(session_id: str, request: ModelPredictRequest):
    """Make prediction using a trained model."""
    import pickle
    import numpy as np
    
    model_path = f"models/{session_id}_best_model.pkl"
    
    try:
        with open(model_path, 'rb') as f:
            saved = pickle.load(f)
        
        model = saved['model']
        feature_columns = saved['feature_columns']
        
        # Build feature vector
        input_data = pd.DataFrame([request.data])
        
        # Ensure correct columns
        for col in feature_columns:
            if col not in input_data.columns:
                input_data[col] = 0
        
        input_data = input_data[feature_columns]
        
        prediction = model.predict(input_data)
        
        result = {
            "success": True,
            "prediction": prediction.tolist(),
            "model_used": saved['model_name'],
            "problem_type": saved['problem_type']
        }
        
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(input_data)
            result['probabilities'] = proba.tolist()
        
        return JSONResponse(content=result)
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Trained model not found for this session")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
