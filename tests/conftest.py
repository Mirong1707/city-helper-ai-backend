"""Pytest configuration and fixtures"""

import pytest
from dotenv import load_dotenv

from app.services.openai_service import OpenAIService

# Load environment variables for tests
load_dotenv()


@pytest.fixture(scope="session")
def openai_service():
    """
    Create OpenAIService instance for integration tests

    Requires SECRET_OPENAI_API_KEY in environment
    """
    service = OpenAIService()

    if not service.is_available():
        pytest.skip("OpenAI API key not configured - skipping integration tests")

    return service


@pytest.fixture
def mock_previous_response_bars():
    """Mock previous response with 5 bars in Munich"""
    return """Great choice! I've selected 5 interesting places for you:

1. **Hofbräuhaus München** - Famous beer hall...
2. **Augustiner-Keller** - Traditional beer garden...
3. **Paulaner Bräuhaus** - Brewery restaurant...
4. **Schumann's Bar** - Classic cocktail bar...
5. **Giesinger Bräu** - Craft brewery..."""


@pytest.fixture
def mock_previous_response_parks():
    """Mock previous response with 3 parks in Paris"""
    return """Great choice! I've selected 3 interesting places for you:

1. **Tuileries Garden** - Historic garden between Louvre...
2. **Jardin du Luxembourg** - Beautiful park with palace...
3. **Parc Monceau** - Elegant park with statues..."""


@pytest.fixture
def mock_previous_request_bars():
    """Mock previous request for bars in Munich"""
    return "Top 5 bars in Munich"


@pytest.fixture
def mock_previous_request_parks():
    """Mock previous request for parks in Paris"""
    return "Best parks in Paris"
