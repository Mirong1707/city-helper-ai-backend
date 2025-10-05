"""Chat-related schemas"""

from typing import Any

from pydantic import BaseModel


class ChatMessageRequest(BaseModel):
    """Request schema for sending a chat message"""

    message: str


class ChatMessageResponse(BaseModel):
    """Response schema for chat messages"""

    response: str
    workspace: Any
