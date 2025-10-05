"""Chat session management service"""

import random
import time
from datetime import datetime

from fastapi import HTTPException


class ChatSessionService:
    """Service for managing chat sessions"""

    def __init__(self):
        # In-memory storage (replace with DB in future)
        self.sessions_db: dict = {}

    def get_all_sessions(self, delay: float = 0.3) -> list[dict]:
        """
        Get all chat sessions sorted by update time

        Args:
            delay: Network delay simulation

        Returns:
            List of chat sessions
        """
        time.sleep(delay)

        sessions = list(self.sessions_db.values())
        sessions.sort(key=lambda x: x["updated_at"], reverse=True)

        return sessions

    def create_session(
        self, title: str, messages: list, workspace_content: dict, delay: float = 0.3
    ) -> dict:
        """
        Create new chat session

        Args:
            title: Session title
            messages: Initial messages
            workspace_content: Initial workspace content
            delay: Network delay simulation

        Returns:
            Created session
        """
        time.sleep(delay)

        session_id = self._generate_session_id()
        now = datetime.now().isoformat()

        new_session = {
            "id": session_id,
            "title": title,
            "messages": messages,
            "workspaceContent": workspace_content,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now,
        }

        self.sessions_db[session_id] = new_session

        return new_session

    def update_session(
        self, session_id: str, messages: list, workspace_content: dict, delay: float = 0.3
    ) -> dict:
        """
        Update existing chat session

        Args:
            session_id: Session ID
            messages: Updated messages
            workspace_content: Updated workspace content
            delay: Network delay simulation

        Returns:
            Updated session

        Raises:
            HTTPException: If session not found
        """
        time.sleep(delay)

        session = self.sessions_db.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        session["messages"] = messages
        session["workspaceContent"] = workspace_content
        session["updated_at"] = datetime.now().isoformat()

        self.sessions_db[session_id] = session

        return session

    def toggle_favorite(self, session_id: str, delay: float = 0.2) -> dict:
        """
        Toggle favorite status of a session

        Args:
            session_id: Session ID
            delay: Network delay simulation

        Returns:
            Updated session

        Raises:
            HTTPException: If session not found
        """
        time.sleep(delay)

        session = self.sessions_db.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        session["is_favorite"] = not session["is_favorite"]
        session["updated_at"] = datetime.now().isoformat()

        self.sessions_db[session_id] = session

        return session

    def delete_session(self, session_id: str, delay: float = 0.3) -> None:
        """
        Delete chat session

        Args:
            session_id: Session ID
            delay: Network delay simulation

        Raises:
            HTTPException: If session not found
        """
        time.sleep(delay)

        session = self.sessions_db.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        del self.sessions_db[session_id]

    @staticmethod
    def _generate_session_id() -> str:
        """Generate random session ID"""
        return f"session-{int(time.time() * 1000)}-{random.randint(100000, 999999)}"
