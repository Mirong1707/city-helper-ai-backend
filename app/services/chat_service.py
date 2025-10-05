"""Chat service for message processing"""

import time

import structlog

from app.utils.mock_data import MockDataGenerator

logger = structlog.get_logger()


class ChatService:
    """Service for handling chat message logic"""

    def __init__(self):
        self.data_generator = MockDataGenerator()

    def process_message(self, message: str, delay: float = 1.5) -> dict:
        """
        Process incoming chat message and generate response

        Args:
            message: User message
            delay: Network delay simulation

        Returns:
            Dictionary with response and workspace data
        """
        logger.debug("processing_message", message_length=len(message))
        time.sleep(delay)

        message_lower = message.lower()

        # Checklist keywords
        if any(
            keyword in message_lower
            for keyword in ["список", "дел", "задач", "переезд", "счёт", "банк"]
        ):
            logger.info("generated_response", response_type="checklist")
            return {
                "response": "🚀 [BACKEND RESPONSE] Я подготовил для вас чек-лист основных задач после переезда (с любовью от FastAPI 🐍). В правой панели вы можете отмечать выполненные пункты и следить за прогрессом. Не забудьте пункт про питона!",
                "workspace": {
                    "type": "checklist",
                    "data": self.data_generator.generate_checklist(),
                },
            }

        # Map/route keywords
        if any(keyword in message_lower for keyword in ["маршрут", "прогулк", "досуг", "карт"]):
            logger.info("generated_response", response_type="map")
            return {
                "response": "🚀 [BACKEND RESPONSE] Я составил для вас пешеходный маршрут на 2 часа по центру Мюнхена (эксклюзивно от бэкенд-сервера! ⚡). На карте справа отмечены все ЧЕТЫРЕ точки интереса, включая секретное Python Cafe. Приятной прогулки!",
                "workspace": {"type": "map", "data": self.data_generator.generate_map()},
            }

        # Default response
        logger.info("generated_response", response_type="default")
        return {
            "response": "👋 Привет! Я бэкенд на FastAPI 🐍, и я могу помочь вам с организацией дел после переезда или составить маршрут для прогулки. Что вас больше интересует? (P.S. Если видите это сообщение, значит вы успешно подключены к backend серверу!)",
            "workspace": {"type": "empty"},
        }
