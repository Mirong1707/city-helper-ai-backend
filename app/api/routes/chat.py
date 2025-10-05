"""Chat message endpoints"""

from fastapi import APIRouter

from app.core.config import settings

config = settings.config
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse
from app.services import chat_service

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(request: ChatMessageRequest):
    """
    Process chat message and generate AI response

    Args:
        request: User message

    Returns:
        AI response with workspace content
    """
    response_data = chat_service.process_message(message=request.message, delay=config.chat_delay)

    return ChatMessageResponse(**response_data)
