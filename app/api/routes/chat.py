"""Chat message endpoints"""

from fastapi import APIRouter

from app.schemas.chat import ChatMessageRequest, ChatMessageResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Initialize chat service singleton
chat_service = ChatService()


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(request: ChatMessageRequest):
    """
    Process chat message and generate AI response

    Uses full AI pipeline if API keys are configured,
    otherwise falls back to mock responses.

    Args:
        request: User message

    Returns:
        AI response with workspace content
    """
    response_data = await chat_service.process_message(
        message=request.message,
        previous_request=request.previous_request,
        previous_response=request.previous_response,
    )

    return ChatMessageResponse(**response_data)
