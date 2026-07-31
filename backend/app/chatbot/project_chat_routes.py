"""
AI Project Docs Assistant API Routes
Endpoints: chat, history, reset
(DatasetChatAssistant ke chat.py router jaisa hi pattern follow karta hai)
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.chatbot.project_docs_service import ProjectDocsAssistant
from app.auth.dependencies import get_current_user
from app.auth.models import User

router = APIRouter(prefix="/project-chat", tags=["AI Project Docs Assistant"])

# In-memory session (production mein Redis use karna better hoga —
# jaisa DatasetChatAssistant mein bhi comment kiya gaya hai)
_project_chat_sessions: dict = {}


class ProjectChatRequest(BaseModel):
    message: str


def get_or_create_session(user: User) -> ProjectDocsAssistant:
    """Har user ka apna conversation session — dataset chatbot jaisa hi pattern."""
    key = f"project_docs_{user.id}"
    if key not in _project_chat_sessions:
        _project_chat_sessions[key] = ProjectDocsAssistant()
    return _project_chat_sessions[key]


@router.post("/message")
async def send_project_message(
    request: ProjectChatRequest,
    current_user: User = Depends(get_current_user),
):
    """
    User ke sawal ka jawab project documentation (README + code
    docstrings) se RAG ke through deta hai.
    """
    try:
        assistant = get_or_create_session(current_user)
        result = assistant.chat(request.message)
        return {
            "status": "success",
            "user_message": request.message,
            "assistant_response": result["answer"],
            "sources": result["sources"],  # kis file se jawab aaya, transparency ke liye
        }
    except RuntimeError as e:
        # Knowledge base build nahi hui abhi tak
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.get("/history")
async def get_project_chat_history(current_user: User = Depends(get_current_user)):
    """Is user ki project-chat conversation history."""
    key = f"project_docs_{current_user.id}"
    if key not in _project_chat_sessions:
        return {"history": []}
    return {"history": _project_chat_sessions[key].get_conversation_history()}


@router.post("/reset")
async def reset_project_chat(current_user: User = Depends(get_current_user)):
    """Conversation history reset karo."""
    key = f"project_docs_{current_user.id}"
    if key in _project_chat_sessions:
        _project_chat_sessions[key].reset_conversation()
    return {"status": "success", "message": "Project chat conversation reset ho gayi"}
