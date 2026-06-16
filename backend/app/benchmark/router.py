"""
Module 2 - Benchmark Router
Expose leaderboard comparison and model ranking
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import json
import logging

from ..database.connection import get_db

router = APIRouter(prefix="/api/benchmark", tags=["Benchmark"])
logger = logging.getLogger(__name__)


@router.get("/leaderboard/{session_id}")
async def get_benchmark_leaderboard(session_id: str, db: Session = Depends(get_db)):
    """
    Get detailed benchmark leaderboard for a training session.
    Shows all models with full metrics comparison table.
    """
    try:
        from ..datasets.models_module2 import TrainingSession

        session = db.query(TrainingSession).filter(
            TrainingSession.session_id == session_id
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        results = json.loads(session.results)
        leaderboard = results.get("leaderboard", [])

        # Build comparison table
        comparison = {
            "session_id": session_id,
            "problem_type": session.problem_type,
            "best_model": session.best_model,
            "best_score": session.best_score,
            "total_models": len(leaderboard),
            "leaderboard": leaderboard,
            "summary": _build_summary_stats(leaderboard, session.problem_type)
        }

        return JSONResponse(content={"success": True, **comparison})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compare")
async def compare_sessions(
    session_ids: str,  # comma-separated
    db: Session = Depends(get_db)
):
    """Compare best models across multiple training sessions."""
    try:
        from ..datasets.models_module2 import TrainingSession

        ids = [s.strip() for s in session_ids.split(",")]
        comparison_data = []

        for sid in ids:
            session = db.query(TrainingSession).filter(
                TrainingSession.session_id == sid
            ).first()
            if session:
                comparison_data.append({
                    "session_id": sid,
                    "best_model": session.best_model,
                    "best_score": session.best_score,
                    "problem_type": session.problem_type,
                    "created_at": str(session.created_at)
                })

        return JSONResponse(content={
            "success": True,
            "comparison": comparison_data
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_training_history(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get recent training history with best scores."""
    try:
        from ..datasets.models_module2 import TrainingSession

        sessions = db.query(TrainingSession).filter(
            TrainingSession.status == "completed"
        ).order_by(TrainingSession.created_at.desc()).limit(limit).all()

        history = []
        for s in sessions:
            history.append({
                "session_id": s.session_id,
                "best_model": s.best_model,
                "best_score": round(float(s.best_score or 0), 4),
                "problem_type": s.problem_type,
                "target_column": s.target_column,
                "created_at": str(s.created_at)
            })

        return JSONResponse(content={"success": True, "history": history})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _build_summary_stats(leaderboard: list, problem_type: str) -> dict:
    """Build summary statistics from leaderboard."""
    if not leaderboard:
        return {}

    if problem_type == "classification":
        key = "accuracy"
    else:
        key = "r2_score"

    scores = [m["metrics"].get(key, 0) for m in leaderboard if m.get("metrics")]

    return {
        "metric": key,
        "best": round(max(scores), 4) if scores else 0,
        "worst": round(min(scores), 4) if scores else 0,
        "mean": round(sum(scores) / len(scores), 4) if scores else 0,
        "gap": round((max(scores) - min(scores)), 4) if scores else 0,
        "models_above_90pct": sum(1 for s in scores if s >= 0.9)
    }
