"""
AI Chat Assistant API Routes
Endpoints: chat, quick insights, conversation history, reset
"""
import pandas as pd
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.chatbot.chat_service import DatasetChatAssistant
from app.auth.dependencies import get_current_user
from app.database.connection import get_db
from app.auth.models import User
from app.datasets.models import Dataset, DatasetVersion

router = APIRouter(prefix="/chat", tags=["AI Chat Assistant"])
UPLOADS_DIR = Path("uploads")

# In-memory sessions (use Redis in production)
_chat_sessions: dict = {}


class ChatRequest(BaseModel):
    dataset_id: int
    message: str
    session_id: Optional[str] = None


class ResetRequest(BaseModel):
    dataset_id: int
    session_id: Optional[str] = None


def load_dataset(dataset_id: int, db: Session, user: User) -> pd.DataFrame:
    """Load dataset CSV/Excel using the active version's file path."""
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
        raise HTTPException(status_code=500, detail="Could not decode CSV file with any known encoding")
    return pd.read_excel(version.file_path)


def get_or_create_session(dataset_id: int, user: User, db: Session) -> DatasetChatAssistant:
    """Get existing chat session or create a new one."""
    key = f"{user.id}_{dataset_id}"
    if key not in _chat_sessions:
        df = load_dataset(dataset_id, db, user)
        _chat_sessions[key] = DatasetChatAssistant(df, dataset_name=f"Dataset #{dataset_id}")
    return _chat_sessions[key]


@router.post("/message")
async def send_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to the AI dataset assistant.
    The AI has full context of your dataset.
    """
    try:
        assistant = get_or_create_session(request.dataset_id, current_user, db)
        response = assistant.chat(request.message)
        return {
            "status": "success",
            "dataset_id": request.dataset_id,
            "user_message": request.message,
            "assistant_response": response
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.get("/insights/{dataset_id}")
async def get_quick_insights(
    dataset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Auto-generate AI insights about your dataset without asking a question.
    Returns key observations, ML task suggestions, and quality concerns.
    """
    try:
        assistant = get_or_create_session(dataset_id, current_user, db)
        insights = assistant.get_quick_insights()
        return {
            "status": "success",
            "dataset_id": dataset_id,
            "insights": insights
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{dataset_id}")
async def get_chat_history(
    dataset_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get full conversation history for this dataset session."""
    key = f"{current_user.id}_{dataset_id}"
    if key not in _chat_sessions:
        return {"dataset_id": dataset_id, "history": []}
    history = _chat_sessions[key].get_conversation_history()
    return {"dataset_id": dataset_id, "history": history}


@router.post("/reset")
async def reset_conversation(
    request: ResetRequest,
    current_user: User = Depends(get_current_user)
):
    """Reset conversation history for a dataset session."""
    key = f"{current_user.id}_{request.dataset_id}"
    if key in _chat_sessions:
        _chat_sessions[key].reset_conversation()
    return {"status": "success", "message": "Conversation reset successfully"}