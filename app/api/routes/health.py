"""Health check endpoint"""

from datetime import datetime

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Health check endpoint to verify server is running"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}
