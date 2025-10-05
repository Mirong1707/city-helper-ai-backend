"""Chat session management endpoints"""

from fastapi import APIRouter

from app.core.config import settings

config = settings.config
from app.schemas.chat_session import (
    ChatSession,
    CreateChatSessionRequest,
    UpdateChatSessionRequest,
)
from app.services import chat_session_service

router = APIRouter(prefix="/api/chat-sessions", tags=["chat-sessions"])


@router.get("", response_model=list[ChatSession])
async def get_sessions():
    """
    Get all chat sessions

    Returns:
        List of chat sessions sorted by update time
    """
    return chat_session_service.get_all_sessions(delay=config.session_delay)


@router.post("", response_model=ChatSession)
async def create_session(request: CreateChatSessionRequest):
    """
    Create new chat session

    Args:
        request: Session creation data

    Returns:
        Created session
    """
    session = chat_session_service.create_session(
        title=request.title,
        messages=request.messages,
        workspace_content=request.workspaceContent,
        delay=config.session_delay,
    )

    return ChatSession(**session)


@router.patch("/{session_id}", response_model=ChatSession)
async def update_session(session_id: str, request: UpdateChatSessionRequest):
    """
    Update existing chat session

    Args:
        session_id: Session ID
        request: Update data

    Returns:
        Updated session

    Raises:
        HTTPException 404: If session not found
    """
    session = chat_session_service.update_session(
        session_id=session_id,
        messages=request.messages,
        workspace_content=request.workspaceContent,
        delay=config.session_delay,
    )

    return ChatSession(**session)


@router.patch("/{session_id}/favorite", response_model=ChatSession)
async def toggle_favorite(session_id: str):
    """
    Toggle favorite status of session

    Args:
        session_id: Session ID

    Returns:
        Updated session

    Raises:
        HTTPException 404: If session not found
    """
    session = chat_session_service.toggle_favorite(session_id=session_id, delay=0.2)

    return ChatSession(**session)


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """
    Delete chat session

    Args:
        session_id: Session ID

    Returns:
        Success message

    Raises:
        HTTPException 404: If session not found
    """
    chat_session_service.delete_session(session_id=session_id, delay=config.session_delay)

    return {"message": "Session deleted successfully"}
