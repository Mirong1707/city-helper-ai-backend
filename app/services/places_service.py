"""Google Places API service for location data"""

import unicodedata

import httpx
import structlog

from app.core.config import settings
from app.schemas.agent import EnrichedPlace, PlaceCoordinates, PlaceSuggestion

logger = structlog.get_logger()


class PlacesService:
    """Service for interacting with Google Places API"""

    def __init__(self):
        """Initialize Places service"""
        self.api_key = settings.secrets.get_google_api_key()
        self.base_url = "https://places.googleapis.com/v1"

        if not self.api_key:
            logger.warning("google_api_key_not_configured")
        else:
            logger.info("places_service_initialized")

    def is_available(self) -> bool:
        """Check if Google Places service is configured"""
        return self.api_key is not None

    def _normalize_city_name(self, city: str) -> str:
        """
        Normalize city name for comparison
        - Remove accents/diacritics (München → Munchen, São Paulo → Sao Paulo)
        - Convert to lowercase
        - Remove common suffixes/prefixes
        """
        # Remove accents/diacritics
        normalized = unicodedata.normalize("NFD", city)
        normalized = "".join(char for char in normalized if unicodedata.category(char) != "Mn")

        # Lowercase and strip
        return normalized.lower().strip()

    def _is_city_in_address(self, requested_city: str, address: str) -> bool:
        """
        Smart city matching without hardcoded mappings

        Uses multiple strategies:
        1. Exact match (case-insensitive)
        2. Normalized match (removes accents: München → Munchen)
        3. Substring match (handles "Saint Petersburg" vs "Sankt-Peterburg")
        4. Edit distance for typos/variations

        Args:
            requested_city: City name from user request
            address: Full address from Google Maps

        Returns:
            True if the address likely belongs to the requested city
        """
        address_lower = address.lower()
        city_lower = requested_city.lower().strip()

        # Strategy 1: Exact substring match
        if city_lower in address_lower:
            return True

        # Strategy 2: Normalized match (remove accents)
        city_normalized = self._normalize_city_name(requested_city)
        address_normalized = self._normalize_city_name(address)

        if city_normalized in address_normalized:
            return True

        # Strategy 3: Check if city is a significant part of address
        # Split address into tokens and check each
        address_tokens = address_lower.replace(",", " ").split()

        for token in address_tokens:
            # Remove common suffixes
            token_clean = token.strip(".,;-")

            if not token_clean or len(token_clean) < 3:
                continue

            # Check if token is very similar to city name
            if token_clean == city_lower:
                return True

            # Check normalized token
            token_normalized = self._normalize_city_name(token_clean)
            if token_normalized == city_normalized:
                return True

            # Strategy 4: Edit distance for close matches
            # Allow small differences (e.g., Lisboa vs Lisbon = distance 3, Moscow vs Moskva = distance 3)
            if len(city_normalized) >= 4:
                distance = self._levenshtein_distance(city_normalized, token_normalized)
                # Allow 30% difference OR minimum 3 for cities with 6+ letters
                max_allowed_distance = max(3, len(city_normalized) // 3)

                if distance <= max_allowed_distance:
                    return True

        return False

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        Calculate Levenshtein distance between two strings
        (minimum number of edits to transform s1 into s2)
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # Cost of insertions, deletions, or substitutions
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    async def search_place(self, place_name: str, location: str) -> dict | None:
        """
        Search for a specific place using Google Places Text Search

        Args:
            place_name: Name of the place to search
            location: City or area to search in

        Returns:
            Place data dict or None if not found
        """
        if not self.is_available():
            logger.warning("places_api_not_available")
            return None

        # Build search query with location bias
        # Try with full context first: "Place Name, City"
        search_query = f"{place_name}, {location}"

        logger.debug("searching_place", query=search_query, location=location)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/places:searchText",
                    headers={
                        "Content-Type": "application/json",
                        "X-Goog-Api-Key": self.api_key,
                        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.googleMapsUri,places.photos",
                    },
                    json={"textQuery": search_query, "maxResultCount": 1},
                    timeout=10.0,
                )

                if response.status_code != 200:
                    logger.error(
                        "places_search_failed",
                        status_code=response.status_code,
                        response=response.text,
                    )
                    return None

                data = response.json()
                places = data.get("places", [])

                if not places:
                    logger.warning(
                        "⚠️ Place NOT found on Google Maps", query=search_query, location=location
                    )
                    return None

                place = places[0]
                place_name = place.get("displayName", {}).get("text")
                logger.info(
                    "✅ Place FOUND on Google Maps",
                    name=place_name,
                    address=place.get("formattedAddress", "N/A")[:50],
                )

                return place

        except Exception as e:
            logger.error("place_search_error", error=str(e), query=search_query)
            return None

    async def enrich_place(
        self, suggestion: PlaceSuggestion, location: str
    ) -> EnrichedPlace | None:
        """
        Enrich a place suggestion with real location data from Google Places

        Args:
            suggestion: Place suggestion from AI
            location: City/area context

        Returns:
            EnrichedPlace with coordinates and real data, or None if not found
        """
        place_data = await self.search_place(suggestion.name, location)

        if not place_data:
            return None

        try:
            # Extract data from Google Places response
            place_id = place_data.get("id", "")
            display_name = place_data.get("displayName", {}).get("text", suggestion.name)
            address = place_data.get("formattedAddress", "Address not available")

            # CRITICAL CHECK: Verify place is actually in the requested city
            # Use smart city matching (no hardcoded mappings!)
            city_in_address = self._is_city_in_address(location, address)

            if not city_in_address:
                logger.warning(
                    "❌ Place REJECTED - not in requested city",
                    place_name=display_name,
                    requested_city=location,
                    actual_address=address[:80],
                )
                return None

            location_data = place_data.get("location", {})
            coordinates = PlaceCoordinates(
                lat=location_data.get("latitude", 0.0), lng=location_data.get("longitude", 0.0)
            )

            rating = place_data.get("rating")
            user_ratings_total = place_data.get("userRatingCount")
            google_maps_link = place_data.get("googleMapsUri", "")

            # Get photo URL if available
            photo_url = None
            photos = place_data.get("photos", [])
            if photos and len(photos) > 0:
                photo_name = photos[0].get("name", "")
                if photo_name:
                    # Photo URL format: https://places.googleapis.com/v1/{name}/media?key=API_KEY&maxHeightPx=400
                    photo_url = f"https://places.googleapis.com/v1/{photo_name}/media?key={self.api_key}&maxHeightPx=400"

            enriched = EnrichedPlace(
                name=display_name,
                description=suggestion.short_description,
                address=address,
                coordinates=coordinates,
                place_id=place_id,
                rating=rating,
                user_ratings_total=user_ratings_total,
                google_maps_link=google_maps_link,
                photo_url=photo_url,
            )

            logger.info(
                "place_enriched", name=display_name, rating=rating, has_photo=photo_url is not None
            )

            return enriched

        except Exception as e:
            logger.error("place_enrichment_error", error=str(e), place=suggestion.name)
            return None

    async def enrich_places(
        self, suggestions: list[PlaceSuggestion], location: str
    ) -> list[EnrichedPlace]:
        """
        Enrich multiple place suggestions with real location data

        Args:
            suggestions: List of place suggestions from AI
            location: City/area context

        Returns:
            List of enriched places (only successfully enriched ones)
        """
        logger.info("enriching_places", count=len(suggestions), location=location)

        enriched_places = []

        for suggestion in suggestions:
            enriched = await self.enrich_place(suggestion, location)
            if enriched:
                enriched_places.append(enriched)

        logger.info(
            "places_enrichment_complete", requested=len(suggestions), enriched=len(enriched_places)
        )

        return enriched_places

    def get_place_url(self, place_id: str) -> str:
        """
        Generate Google Maps URL for a place

        Args:
            place_id: Google Place ID

        Returns:
            Google Maps URL
        """
        return f"https://www.google.com/maps/place/?q=place_id:{place_id}"
