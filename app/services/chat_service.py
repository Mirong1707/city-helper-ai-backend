"""Chat service for message processing with AI agent pipeline"""

import math
import re

import structlog

from app.schemas.agent import EnrichedPlace, QueryClassification
from app.services.maps_service import MapsService
from app.services.openai_service import OpenAIService
from app.services.places_service import PlacesService
from app.utils.mock_data import MockDataGenerator

logger = structlog.get_logger()


def extract_places_from_response(response_text: str) -> list | None:
    """
    Extract place names from previous AI response

    Args:
        response_text: Previous AI response text

    Returns:
        List of place names or None
    """
    if not response_text:
        return None

    # Pattern to match numbered list items like "1. **Place Name** - description"
    pattern = r"\d+\.\s+\*\*([^*]+)\*\*"
    matches = re.findall(pattern, response_text)

    if matches:
        logger.debug("extracted_places_from_previous_response", count=len(matches), places=matches)
        return matches

    return None


def calculate_distance(place1: EnrichedPlace, place2: EnrichedPlace) -> float:
    """Calculate Haversine distance between two places in kilometers"""
    lat1, lon1 = place1.coordinates.lat, place1.coordinates.lng
    lat2, lon2 = place2.coordinates.lat, place2.coordinates.lng

    radius_earth = 6371  # Earth radius in kilometers

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))

    return radius_earth * c


def optimize_route_greedy(places: list[EnrichedPlace]) -> list[EnrichedPlace]:
    """
    Optimize route using greedy nearest-neighbor algorithm

    Starts from first place and always goes to nearest unvisited place.
    This gives a ~90% optimal solution very quickly.

    Args:
        places: List of enriched places

    Returns:
        Reordered list of places for optimal route
    """
    if len(places) <= 2:
        return places  # No optimization needed

    optimized = [places[0]]  # Start from first place
    remaining = places[1:]

    while remaining:
        current = optimized[-1]
        # Find nearest unvisited place
        nearest = min(remaining, key=lambda p: calculate_distance(current, p))
        optimized.append(nearest)
        remaining.remove(nearest)

    logger.info(
        "route_optimized",
        original_order=[p.name for p in places],
        optimized_order=[p.name for p in optimized],
    )

    return optimized


class ChatService:
    """
    Service for handling chat message logic

    Orchestrates the full AI agent pipeline:
    1. Query classification (OpenAI)
    2. Place suggestions (OpenAI)
    3. Place enrichment (Google Places)
    4. Map generation (Google Maps)
    """

    def __init__(self):
        """Initialize chat service with all sub-services"""
        self.openai_service = OpenAIService()
        self.places_service = PlacesService()
        self.maps_service = MapsService()
        self.mock_generator = MockDataGenerator()

        # Check if AI features are available
        self.ai_enabled = (
            self.openai_service.is_available()
            and self.places_service.is_available()
            and self.maps_service.is_available()
        )

        if self.ai_enabled:
            logger.info("chat_service_initialized", mode="AI")
        else:
            logger.warning(
                "chat_service_fallback_mode",
                message="Running in mock mode - API keys not configured",
            )

    async def process_message(
        self,
        message: str,
        previous_request: str | None = None,
        previous_response: str | None = None,
    ) -> dict:
        """
        Process incoming chat message and generate response

        Args:
            message: User message

        Returns:
            Dictionary with response and workspace data
        """
        logger.info(
            "💬 NEW MESSAGE RECEIVED",
            message=message[:100],
            ai_enabled=self.ai_enabled,
            mode="AI" if self.ai_enabled else "MOCK",
        )

        # If AI is enabled, use the full pipeline
        if self.ai_enabled:
            try:
                return await self._process_with_ai(message, previous_request, previous_response)
            except Exception as e:
                logger.error(
                    "💥 AI PROCESSING FAILED",
                    error=str(e),
                    error_type=type(e).__name__,
                    exc_info=True,
                )
                return self._fallback_response(
                    "Sorry, an error occurred while processing your request. Please try again."
                )

        # Otherwise, use mock responses
        return self._process_with_mock(message)

    async def _apply_agent_routing(
        self,
        message: str,
        classification: QueryClassification,
        previous_request: str | None,
        previous_response: str | None,
    ) -> tuple:
        """Apply agent-based routing to determine operation type and adjust count"""
        previous_places_list = (
            extract_places_from_response(previous_response) if previous_response else None
        )
        previous_count = len(previous_places_list) if previous_places_list else 0

        routing = await self.openai_service.route_request(
            current_message=message,
            previous_request=previous_request,
            previous_response=previous_response,
            previous_places_count=previous_count,
        )

        logger.info(
            "🤖 AGENT ROUTING DECISION",
            is_new=routing.is_new_request,
            operation=routing.operation_type,
            use_context=routing.use_previous_context,
            reasoning=routing.reasoning,
        )

        operation_hint = None
        theme_override = None

        if routing.is_new_request or routing.operation_type == "new":
            previous_places_list = None
            operation_hint = None
        else:
            operation_hint = routing.operation_type

            # Adjust count based on operation
            if routing.operation_type == "add" and routing.count_adjustment:
                classification.count = previous_count + abs(routing.count_adjustment)
                logger.info(
                    "➕ Count adjusted for ADD",
                    old_count=previous_count,
                    new_count=classification.count,
                )
            elif routing.operation_type == "remove" and routing.count_adjustment:
                classification.count = max(1, previous_count - abs(routing.count_adjustment))
                logger.info(
                    "➖ Count adjusted for REMOVE",
                    old_count=previous_count,
                    new_count=classification.count,
                )
            elif routing.operation_type in ["replace_last", "replace_all"]:
                classification.count = max(classification.count, previous_count)

            # Extract theme from message
            message_lower = message.lower()
            if "центр" in message_lower or "center" in message_lower:
                if routing.operation_type in ["replace_last", "replace_all"]:
                    theme_override = "in city center (Marienplatz, Altstadt area)"
                elif routing.operation_type == "add":
                    theme_override = "in city center"

        return previous_places_list, operation_hint, theme_override

    async def _enrich_with_retry(
        self,
        suggestions,
        classification: QueryClassification,
    ) -> list[EnrichedPlace]:
        """Enrich places with Google Places API and retry if needed"""
        enriched_places = await self.places_service.enrich_places(
            suggestions=suggestions.places,
            location=classification.location,
        )

        logger.info(
            "✅ Places enriched",
            requested=classification.count,
            found=len(enriched_places),
            success_rate=f"{len(enriched_places)}/{classification.count}",
        )

        # Retry if we didn't get enough places
        if len(enriched_places) < classification.count:
            missing_count = classification.count - len(enriched_places)
            tried_places = [place.name for place in suggestions.places]

            logger.info(
                "🔄 RETRY - Requesting more places",
                missing=missing_count,
                excluded=tried_places,
            )

            retry_suggestions = await self.openai_service.suggest_places(
                location=classification.location,
                place_type=classification.place_type,
                count=missing_count,
                theme=classification.theme,
                excluded_places=tried_places,
            )

            retry_enriched = await self.places_service.enrich_places(
                suggestions=retry_suggestions.places,
                location=classification.location,
            )

            enriched_places.extend(retry_enriched)
            logger.info("✅ RETRY completed", total_found=len(enriched_places))

        return enriched_places

    async def _process_with_ai(
        self,
        message: str,
        previous_request: str | None = None,
        previous_response: str | None = None,
    ) -> dict:
        """
        Process message using AI agent pipeline

        Pipeline steps:
        1. Classify query to understand intent
        2. If it's a route request, generate place suggestions
        3. Enrich suggestions with real location data
        4. Generate map URLs and format response

        Args:
            message: User message

        Returns:
            Formatted response dict
        """
        logger.info("🚀 AI PIPELINE STARTED", message=message[:100])

        # Step 1: Classify query with context
        logger.info("📊 STEP 1: Classifying user query with OpenAI")
        classification = await self.openai_service.classify_query(
            message, previous_request=previous_request, previous_response=previous_response
        )

        logger.info(
            "✅ Query classified",
            is_route=classification.is_route_request,
            location=classification.location,
            place_type=classification.place_type,
            count=classification.count,
        )

        if not classification.is_route_request:
            logger.info("❌ Not a route request - returning help message")
            return {
                "response": "I'll help you find interesting places in the city! Try asking something like:\n\n• 'Top 5 bars in Munich'\n• '3 contemporary art museums in Berlin'\n• 'Best parks in London for walking'\n\nWhat are you interested in?",
                "workspace": {"type": "empty"},
            }

        # Check if requested count exceeds limit
        if classification.count > 10:
            logger.warning(
                "❌ Requested count exceeds limit", requested=classification.count, max_allowed=10
            )
            return {
                "response": f"Sorry, but our service currently supports up to 10 places per request for the best user experience.\n\nYou requested {classification.count} places, which is quite a lot! 😅\n\nPlease try asking for 10 or fewer places. For example:\n• 'Top 10 {classification.place_type} in {classification.location}'\n• 'Best 5 {classification.place_type} in {classification.location}'\n\nThis helps us create better routes and keep the map readable!",
                "workspace": {"type": "empty"},
            }

        # Step 2: Generate place suggestions with AI and apply routing
        logger.info("🤖 STEP 2: Generating place suggestions with OpenAI")

        previous_places_list, operation_hint, theme_override = await self._apply_agent_routing(
            message, classification, previous_request, previous_response
        )

        suggestions = await self.openai_service.suggest_places(
            location=classification.location,
            place_type=classification.place_type,
            count=classification.count,
            theme=theme_override or classification.theme,
            previous_places=previous_places_list,
            modification_request=message if previous_places_list else None,
            operation_hint=operation_hint,
        )

        logger.info(
            "✅ OpenAI suggested places",
            count=len(suggestions.places),
            places=[p.name for p in suggestions.places],
        )

        if not suggestions.places:
            logger.warning("⚠️ No suggestions generated by OpenAI")
            return self._fallback_response(
                "Unfortunately, couldn't find suitable places. Please try a different query."
            )

        # Step 3: Enrich places with real location data and retry if needed
        logger.info("📍 STEP 3: Enriching places with Google Places API")
        enriched_places = await self._enrich_with_retry(suggestions, classification)

        # Optimize route order (greedy nearest-neighbor)
        if len(enriched_places) > 2:
            logger.info("🔄 STEP 3.5: Optimizing route order")
            enriched_places = optimize_route_greedy(enriched_places)
            logger.info("✅ Route optimized for minimal distance")

        if not enriched_places:
            logger.error("❌ No places found on Google Maps")
            return self._fallback_response(
                f"Couldn't find exact locations for '{classification.place_type}' in {classification.location}. Please try a different query."
            )

        # Step 4: Generate map data
        logger.info(
            "🗺️ STEP 4: Generating map and route data",
            places_count=len(enriched_places),
            travel_mode=classification.travel_mode,
        )

        title = f"{len(enriched_places)} {classification.place_type} in {classification.location}"

        map_data = self.maps_service.generate_map_data(
            places=enriched_places,
            title=title,
            description=suggestions.route_description,
            duration=suggestions.estimated_duration,
            travel_mode=classification.travel_mode,
        )

        logger.info(
            "✅ Map data generated", points=len(map_data.points), segments=len(map_data.segments)
        )

        # Format response message
        places_list = "\n".join(
            [
                f"{i + 1}. **{place.name}** - {place.description[:80]}..."
                for i, place in enumerate(enriched_places)  # Show all places
            ]
        )

        response_text = f"""Great choice! I've selected {len(enriched_places)} interesting places for you:

{places_list}

📍 You'll see all route points on the map on the right.
⏱️ Estimated time: {suggestions.estimated_duration}
🚶 Travel mode: {self._travel_mode_en(classification.travel_mode)}

Click on any point to open it in Google Maps!"""

        logger.info(
            "🎉 AI PIPELINE COMPLETED SUCCESSFULLY",
            places_found=len(enriched_places),
            duration=suggestions.estimated_duration,
            location=classification.location,
        )

        return {
            "response": response_text,
            "workspace": {"type": "map", "data": map_data.model_dump()},
        }

    def _process_with_mock(self, message: str) -> dict:
        """
        Process message using mock data (fallback mode)

        Args:
            message: User message

        Returns:
            Mock response dict
        """
        message_lower = message.lower()

        # Checklist keywords
        if any(
            keyword in message_lower
            for keyword in ["список", "дел", "задач", "переезд", "счёт", "банк"]
        ):
            logger.info("mock_response", response_type="checklist")
            return {
                "response": "🚀 [MOCK MODE] I've prepared a checklist of essential tasks. Add API keys for full functionality.",
                "workspace": {
                    "type": "checklist",
                    "data": self.mock_generator.generate_checklist(),
                },
            }

        # Map/route keywords
        if any(
            keyword in message_lower
            for keyword in ["маршрут", "прогулк", "досуг", "карт", "бар", "музе", "парк"]
        ):
            logger.info("mock_response", response_type="map")
            return {
                "response": "🗺️ [MOCK MODE] Here's a sample route. Add OpenAI and Google API keys to the .env file for real data.",
                "workspace": {"type": "map", "data": self.mock_generator.generate_map()},
            }

        # Default response
        logger.info("mock_response", response_type="default")
        return {
            "response": "👋 Hello! I'm City Helper in demo mode (mock mode). Add API keys to the .env file for full functionality:\n\n• SECRET_OPENAI_API_KEY\n• SECRET_GOOGLE_API_KEY\n\nTry asking about routes, bars, museums, or parks!",
            "workspace": {"type": "empty"},
        }

    def _fallback_response(self, message: str) -> dict:
        """Generate fallback response for errors"""
        return {"response": message, "workspace": {"type": "empty"}}

    def _travel_mode_en(self, mode: str) -> str:
        """Translate travel mode to English"""
        translations = {
            "walking": "walking",
            "driving": "by car",
            "transit": "by public transport",
            "bicycling": "by bicycle",
        }
        return translations.get(mode, mode)
