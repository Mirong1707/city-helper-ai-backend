"""Data schemas for AI agent pipeline"""

from pydantic import BaseModel, Field


class QueryClassification(BaseModel):
    """
    Classification result for user query

    Determines if the user is asking for a route/places recommendation
    and extracts structured parameters
    """

    is_route_request: bool = Field(
        description="Whether this is a request for route/places recommendation"
    )
    location: str = Field(description="City or location name (e.g., 'Munich', 'Saint Petersburg')")
    place_type: str = Field(
        description="Type of places requested (e.g., 'bars', 'museums', 'parks')"
    )
    count: int = Field(default=5, description="Number of places requested", ge=1)
    theme: str | None = Field(
        default=None,
        description="Additional theme or preference (e.g., 'modern art', 'craft beer')",
    )
    travel_mode: str = Field(
        default="walking",
        description="Preferred travel mode: 'walking', 'driving', 'transit', 'bicycling'",
    )


class PlaceSuggestion(BaseModel):
    """Single place suggestion from AI"""

    name: str = Field(description="Name of the place")
    short_description: str = Field(description="Brief description of the place")
    why_recommended: str = Field(description="Why this place is recommended")


class PlaceSuggestions(BaseModel):
    """Collection of place suggestions from AI"""

    places: list[PlaceSuggestion] = Field(description="List of suggested places")
    route_description: str = Field(description="Overall description of the route/experience")
    estimated_duration: str = Field(
        default="2-3 hours", description="Estimated time to complete the route"
    )


class PlaceCoordinates(BaseModel):
    """Geographic coordinates"""

    lat: float = Field(description="Latitude")
    lng: float = Field(description="Longitude")


class EnrichedPlace(BaseModel):
    """
    Place data enriched with real location information from Google Places
    """

    name: str = Field(description="Place name")
    description: str = Field(description="Description from AI")
    address: str = Field(description="Full address")
    coordinates: PlaceCoordinates = Field(description="Latitude and longitude")
    place_id: str = Field(description="Google Places ID")
    rating: float | None = Field(default=None, description="Google rating (0-5)")
    user_ratings_total: int | None = Field(default=None, description="Number of user ratings")
    google_maps_link: str = Field(description="Direct link to Google Maps")
    photo_url: str | None = Field(default=None, description="Photo URL if available")


class MapPoint(BaseModel):
    """Map point for frontend MapView component"""

    name: str
    googleMapsLink: str
    address: str | None = None
    rating: float | None = None
    userRatingsTotal: int | None = None
    photoUrl: str | None = None
    coordinates: PlaceCoordinates | None = None


class MapSegment(BaseModel):
    """Map segment (route between two points) for frontend MapView"""

    from_point: str = Field(alias="from")
    to: str
    mapUrl: str

    class Config:
        populate_by_name = True


class MapData(BaseModel):
    """Complete map data for frontend MapView component"""

    title: str
    description: str
    duration: str
    points: list[MapPoint]
    segments: list[MapSegment]
    fullRouteMapUrl: str
    fullRouteLink: str


class AgentResponse(BaseModel):
    """Final response from agent pipeline"""

    response: str = Field(description="Text message to user")
    workspace: dict = Field(description="Workspace data (type + data)")


class AgentRoutingDecision(BaseModel):
    """
    Agent's decision on how to route the request

    Instead of keyword-based detection, AI agent analyzes context
    and decides the routing strategy
    """

    is_new_request: bool = Field(
        description="Is this a completely NEW request (different location/place_type) or a MODIFICATION?"
    )

    operation_type: str = Field(
        description=(
            "Type of operation if modification: "
            "'add' - add more places to existing list, "
            "'remove' - remove places from list, "
            "'replace_last' - replace only the last item, "
            "'replace_all' - replace all items with new ones, "
            "'refine' - adjust parameters (count/theme/etc), "
            "'new' - completely new request"
        )
    )

    use_previous_context: bool = Field(
        description="Should we use previous places as context for this request?"
    )

    reasoning: str = Field(
        description="Brief explanation of why this routing was chosen (for debugging)"
    )

    location_changed: bool = Field(
        description="Did the location/city change from previous request?"
    )

    place_type_changed: bool = Field(description="Did the place type change from previous request?")

    count_adjustment: int | None = Field(
        default=None,
        description="If operation is add/remove, by how much to adjust count (+N or -N)",
    )
