"""Mock data generators for testing and development"""


class MockDataGenerator:
    """Generator for mock checklist and map data"""

    @staticmethod
    def generate_checklist() -> dict:
        """
        Generate mock checklist data

        Returns:
            Dictionary with checklist structure
        """
        return {
            "title": "🚀 [BACKEND] Что нужно сделать после переезда",
            "description": "⚡ Данные с FastAPI сервера! Основные шаги для комфортного обустройства в новом городе",
            "items": [
                {
                    "id": "1",
                    "title": "🎯 Купить местную SIM-карту для мобильной связи",
                    "completed": False,
                },
                {"id": "2", "title": "💰 Открыть счёт в местном банке", "completed": False},
                {
                    "id": "3",
                    "title": "📝 Зарегистрироваться по новому адресу проживания",
                    "completed": False,
                },
                {
                    "id": "4",
                    "title": "🌐 Подключить домашний интернет (привет от Python!)",
                    "completed": False,
                },
                {
                    "id": "5",
                    "title": "🛒 Найти ближайшие продуктовые магазины и аптеки",
                    "completed": False,
                },
                {
                    "id": "6",
                    "title": "🚌 Изучить систему общественного транспорта",
                    "completed": False,
                },
                {"id": "7", "title": "🐍 Погладить питона (это бэкенд-шутка)", "completed": False},
            ],
        }

    @staticmethod
    def generate_map() -> dict:
        """
        Generate mock map/route data

        Returns:
            Dictionary with map structure
        """
        return {
            "title": "🚀 [BACKEND] Прогулка по центру Мюнхена",
            "description": "⚡ Маршрут создан FastAPI сервером! Пешеходный маршрут на 2 часа с посещением главных достопримечательностей",
            "duration": "2 часа (+ время на селфи с бэкендом 📸)",
            "points": [
                {
                    "name": "🏛️ Мариенплац (начало Python-путешествия)",
                    "googleMapsLink": "https://www.google.com/maps/place/Marienplatz,+München/@48.1374,11.5755,17z",
                },
                {
                    "name": "⛪ Фрауэнкирхе (one API call away)",
                    "googleMapsLink": "https://www.google.com/maps/place/Frauenkirche,+München/@48.1386,11.5733,17z",
                },
                {
                    "name": "🌳 Английский сад (brought to you by FastAPI)",
                    "googleMapsLink": "https://www.google.com/maps/place/Englischer+Garten,+München/@48.1642,11.6050,15z",
                },
                {
                    "name": "🐍 Секретная точка: Python Cafe (только для backend users)",
                    "googleMapsLink": "https://www.google.com/maps/place/München/@48.1351,11.5820,17z",
                },
            ],
            "segments": [
                {
                    "from": "🏛️ Мариенплац",
                    "to": "⛪ Фрауэнкирхе",
                    "mapUrl": "https://www.google.com/maps?output=embed&q=48.1380,11.5744&z=16",
                },
                {
                    "from": "⛪ Фрауэнкирхе",
                    "to": "🌳 Английский сад",
                    "mapUrl": "https://www.google.com/maps?output=embed&q=48.1514,11.5892&z=14",
                },
                {
                    "from": "🌳 Английский сад",
                    "to": "🐍 Python Cafe",
                    "mapUrl": "https://www.google.com/maps?output=embed&q=48.1351,11.5820&z=15",
                },
            ],
            "fullRouteMapUrl": "https://www.google.com/maps?output=embed&q=Marienplatz,München&z=14",
            "fullRouteLink": "https://www.google.com/maps/dir/Marienplatz,+München/Frauenkirche,+München/Englischer+Garten,+München/@48.1514,11.5850,14z",
        }
