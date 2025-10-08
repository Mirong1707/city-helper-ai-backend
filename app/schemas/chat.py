"""Chat-related schemas"""

from typing import Any

from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    """Request schema for sending a chat message"""

    message: str = Field(..., description="User message text")
    previous_request: str | None = Field(None, description="Previous user request for context")
    previous_response: str | None = Field(None, description="Previous AI response for context")


class ChatMessageResponse(BaseModel):
    """Response schema for chat messages"""

    response: str
    workspace: Any
