"""Google Maps URL generation service"""

from urllib.parse import quote

import structlog

from app.core.config import settings
from app.schemas.agent import EnrichedPlace, MapData, MapPoint, MapSegment

logger = structlog.get_logger()


class MapsService:
    """Service for generating Google Maps URLs and embeds"""

    def __init__(self):
        """Initialize Maps service"""
        self.api_key = settings.secrets.get_google_api_key()

        if not self.api_key:
            logger.warning("google_api_key_not_configured_for_maps")
        else:
            logger.info("maps_service_initialized")

    def is_available(self) -> bool:
        """Check if Maps service is configured"""
        return self.api_key is not None

    def generate_place_link(self, place: EnrichedPlace) -> str:
        """
        Generate Google Maps link for a single place

        Args:
            place: Enriched place data

        Returns:
            Google Maps URL - use googleMapsUri from Places API for full place page
        """
        # Use googleMapsUri from Places API - it opens the full place page with reviews
        # If not available, fallback to coordinates format
        if place.google_maps_link:
            return place.google_maps_link

        # Fallback: generate link with coordinates (frontend can still parse it)
        lat = place.coordinates.lat
        lng = place.coordinates.lng
        name = quote(place.name)
        return f"https://www.google.com/maps/place/{name}/@{lat},{lng},15z"

    def generate_directions_url(
        self, origin: EnrichedPlace, destination: EnrichedPlace, travel_mode: str = "walking"
    ) -> str:
        """
        Generate Google Maps directions URL between two places

        Args:
            origin: Starting place
            destination: Ending place
            travel_mode: Travel mode (walking, driving, transit, bicycling)

        Returns:
            Google Maps directions URL
        """
        origin_coords = f"{origin.coordinates.lat},{origin.coordinates.lng}"
        dest_coords = f"{destination.coordinates.lat},{destination.coordinates.lng}"

        return f"https://www.google.com/maps/dir/?api=1&origin={origin_coords}&destination={dest_coords}&travelmode={travel_mode}"

    def generate_embed_url(self, places: list[EnrichedPlace]) -> str:
        """
        Generate Google Maps embed URL for displaying in iframe

        Args:
            places: List of places to display

        Returns:
            Google Maps embed URL
        """
        if not self.api_key:
            logger.warning("cannot_generate_embed_url_without_api_key")
            return ""

        if not places:
            return ""

        if len(places) == 1:
            # Single place mode
            place = places[0]
            lat = place.coordinates.lat
            lng = place.coordinates.lng
            name = quote(place.name)

            return f"https://www.google.com/maps/embed/v1/place?key={self.api_key}&q={name}&center={lat},{lng}&zoom=15"

        # Directions mode - show route through all places
        origin = places[0]
        destination = places[-1]

        origin_coords = f"{origin.coordinates.lat},{origin.coordinates.lng}"
        dest_coords = f"{destination.coordinates.lat},{destination.coordinates.lng}"

        # Add waypoints (middle places)
        waypoints = [f"{place.coordinates.lat},{place.coordinates.lng}" for place in places[1:-1]]
        waypoints_str = "|".join(waypoints) if waypoints else ""

        url = f"https://www.google.com/maps/embed/v1/directions?key={self.api_key}&origin={origin_coords}&destination={dest_coords}&mode=walking"

        if waypoints_str:
            url += f"&waypoints={waypoints_str}"

        return url

    def generate_full_route_link(
        self, places: list[EnrichedPlace], travel_mode: str = "walking"
    ) -> str:
        """
        Generate Google Maps link for full route with all waypoints

        Args:
            places: List of places in order
            travel_mode: Travel mode

        Returns:
            Google Maps directions URL with all waypoints
        """
        if not places:
            return ""

        if len(places) == 1:
            return self.generate_place_link(places[0])

        origin = places[0]
        destination = places[-1]

        origin_coords = f"{origin.coordinates.lat},{origin.coordinates.lng}"
        dest_coords = f"{destination.coordinates.lat},{destination.coordinates.lng}"

        # Build waypoints string
        waypoints = [f"{place.coordinates.lat},{place.coordinates.lng}" for place in places[1:-1]]

        url = f"https://www.google.com/maps/dir/?api=1&origin={origin_coords}&destination={dest_coords}&travelmode={travel_mode}"

        if waypoints:
            waypoints_str = "|".join(waypoints)
            url += f"&waypoints={waypoints_str}"

        return url

    def generate_map_data(
        self,
        places: list[EnrichedPlace],
        title: str,
        description: str,
        duration: str,
        travel_mode: str = "walking",
    ) -> MapData:
        """
        Generate complete MapData for frontend MapView component

        Args:
            places: List of enriched places
            title: Route title
            description: Route description
            duration: Estimated duration
            travel_mode: Travel mode

        Returns:
            MapData object ready for frontend
        """
        logger.info("generating_map_data", places_count=len(places))

        # Generate points for each place
        points: list[MapPoint] = [
            MapPoint(
                name=place.name,
                googleMapsLink=self.generate_place_link(place),
                address=place.address,
                rating=place.rating,
                userRatingsTotal=place.user_ratings_total,
                photoUrl=place.photo_url,
                coordinates=place.coordinates,
            )
            for place in places
        ]

        # Generate segments (routes between consecutive places)
        segments: list[MapSegment] = []
        for i in range(len(places) - 1):
            origin = places[i]
            destination = places[i + 1]

            segment_embed_url = self.generate_embed_url([origin, destination])

            segments.append(
                MapSegment(from_point=origin.name, to=destination.name, mapUrl=segment_embed_url)
            )

        # Generate full route URLs
        full_route_embed = self.generate_embed_url(places, mode="directions")
        full_route_link = self.generate_full_route_link(places, travel_mode)

        map_data = MapData(
            title=title,
            description=description,
            duration=duration,
            points=points,
            segments=segments,
            fullRouteMapUrl=full_route_embed,
            fullRouteLink=full_route_link,
        )

        logger.info("map_data_generated", points_count=len(points), segments_count=len(segments))

        return map_data
