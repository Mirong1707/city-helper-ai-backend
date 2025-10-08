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
            "title": "🚀 [BACKEND] Things to do after moving",
            "description": "⚡ Data from FastAPI server! Essential steps for comfortable settling in your new city",
            "items": [
                {
                    "id": "1",
                    "title": "🎯 Get a local SIM card for mobile service",
                    "completed": False,
                },
                {"id": "2", "title": "💰 Open an account at a local bank", "completed": False},
                {
                    "id": "3",
                    "title": "📝 Register at your new residential address",
                    "completed": False,
                },
                {
                    "id": "4",
                    "title": "🌐 Set up home internet (greetings from Python!)",
                    "completed": False,
                },
                {
                    "id": "5",
                    "title": "🛒 Find nearby grocery stores and pharmacies",
                    "completed": False,
                },
                {
                    "id": "6",
                    "title": "🚌 Learn the public transportation system",
                    "completed": False,
                },
                {"id": "7", "title": "🐍 Pet a python (backend joke)", "completed": False},
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
            "title": "🚀 [BACKEND] Walking tour of Munich center",
            "description": "⚡ Route created by FastAPI server! 2-hour walking route visiting main attractions",
            "duration": "2 hours (+ time for selfies with backend 📸)",
            "points": [
                {
                    "name": "🏛️ Marienplatz (start of Python journey)",
                    "googleMapsLink": "https://www.google.com/maps/place/Marienplatz,+München/@48.1374,11.5755,17z",
                },
                {
                    "name": "⛪ Frauenkirche (one API call away)",
                    "googleMapsLink": "https://www.google.com/maps/place/Frauenkirche,+München/@48.1386,11.5733,17z",
                },
                {
                    "name": "🌳 English Garden (brought to you by FastAPI)",
                    "googleMapsLink": "https://www.google.com/maps/place/Englischer+Garten,+München/@48.1642,11.6050,15z",
                },
                {
                    "name": "🐍 Secret spot: Python Cafe (backend users only)",
                    "googleMapsLink": "https://www.google.com/maps/place/München/@48.1351,11.5820,17z",
                },
            ],
            "segments": [
                {
                    "from": "🏛️ Marienplatz",
                    "to": "⛪ Frauenkirche",
                    "mapUrl": "https://www.google.com/maps?output=embed&q=48.1380,11.5744&z=16",
                },
                {
                    "from": "⛪ Frauenkirche",
                    "to": "🌳 English Garden",
                    "mapUrl": "https://www.google.com/maps?output=embed&q=48.1514,11.5892&z=14",
                },
                {
                    "from": "🌳 English Garden",
                    "to": "🐍 Python Cafe",
                    "mapUrl": "https://www.google.com/maps?output=embed&q=48.1351,11.5820&z=15",
                },
            ],
            "fullRouteMapUrl": "https://www.google.com/maps?output=embed&q=Marienplatz,München&z=14",
            "fullRouteLink": "https://www.google.com/maps/dir/Marienplatz,+München/Frauenkirche,+München/Englischer+Garten,+München/@48.1514,11.5850,14z",
        }
