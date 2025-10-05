"""Chat session schemas"""

from typing import Any

from pydantic import BaseModel


class ChatSession(BaseModel):
    """Chat session model"""

    id: str
    title: str
    messages: list[Any]
    workspaceContent: Any
    is_favorite: bool
    created_at: str
    updated_at: str


class CreateChatSessionRequest(BaseModel):
    """Request schema for creating a chat session"""

    title: str
    messages: list[Any]
    workspaceContent: Any


class UpdateChatSessionRequest(BaseModel):
    """Request schema for updating a chat session"""

    messages: list[Any]
    workspaceContent: Any
