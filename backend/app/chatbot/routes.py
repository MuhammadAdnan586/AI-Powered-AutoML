"""
AI Chat Assistant API Routes
Endpoints: chat, quick insights, conversation history, reset
"""
import pandas as pd
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.chatbot.chat_service import DatasetChatAssistant
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/chat", tags=["AI Chat Assistant"])

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


def get_or_create_session(dataset_id: int, user_id: int) -> DatasetChatAssistant:
    """Get existing chat session or create a new one."""
    key = f"{user_id}_{dataset_id}"
    if key not in _chat_sessions:
        df = load_dataset(dataset_id)
        _chat_sessions[key] = DatasetChatAssistant(df, dataset_name=f"Dataset #{dataset_id}")
    return _chat_sessions[key]


def load_dataset(dataset_id: int) -> pd.DataFrame:
    for ext in [".csv", ".xlsx", ".xls"]:
        path = UPLOADS_DIR / f"dataset_{dataset_id}{ext}"
        if path.exists():
            return pd.read_csv(path) if ext == ".csv" else pd.read_excel(path)
    raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")


@router.post("/message")
async def send_message(
    request: ChatRequest,
    current_user=Depends(get_current_user)
):
    """
    Send a message to the AI dataset assistant.
    The AI has full context of your dataset.
    """
    try:
        assistant = get_or_create_session(request.dataset_id, current_user.id)
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
    current_user=Depends(get_current_user)
):
    """
    Auto-generate AI insights about your dataset without asking a question.
    Returns key observations, ML task suggestions, and quality concerns.
    """
    try:
        assistant = get_or_create_session(dataset_id, current_user.id)
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
    current_user=Depends(get_current_user)
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
    current_user=Depends(get_current_user)
):
    """Reset conversation history for a dataset session."""
    key = f"{current_user.id}_{request.dataset_id}"
    if key in _chat_sessions:
        _chat_sessions[key].reset_conversation()

    return {"status": "success", "message": "Conversation reset successfully"}
