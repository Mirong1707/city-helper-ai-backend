"""OpenAI API service for AI agent operations"""

import structlog
from openai import AsyncOpenAI, OpenAI

from app.core.config import settings
from app.schemas.agent import AgentRoutingDecision, PlaceSuggestions, QueryClassification

logger = structlog.get_logger()


class OpenAIService:
    """Service for interacting with OpenAI API"""

    def __init__(self):
        """Initialize OpenAI client"""
        api_key = settings.secrets.get_openai_api_key()

        if not api_key:
            logger.warning("openai_key_not_configured", message="OpenAI API key not found")
            self.client = None
            self.async_client = None
        else:
            self.client = OpenAI(api_key=api_key)
            self.async_client = AsyncOpenAI(api_key=api_key)
            logger.info("openai_service_initialized")

    def is_available(self) -> bool:
        """Check if OpenAI service is configured and available"""
        return self.client is not None

    async def classify_query(
        self,
        user_message: str,
        previous_request: str | None = None,
        previous_response: str | None = None,
    ) -> QueryClassification:
        """
        Classify user query and extract structured parameters

        Args:
            user_message: Raw user message

        Returns:
            QueryClassification with extracted parameters

        Raises:
            ValueError: If OpenAI is not configured
        """
        if not self.is_available():
            raise ValueError("OpenAI service is not configured")

        logger.debug(
            "classifying_query",
            message_length=len(user_message),
            has_context=previous_request is not None,
        )

        # Build messages with context if available
        messages = [
            {
                "role": "system",
                "content": """You are a query classifier for a city helper app.
Analyze the user's message and determine:
1. Is this a request for places/route recommendation?
2. Extract: location (city), place_type (bars/museums/parks/etc), count, theme, travel_mode

IMPORTANT: Always return city names in ENGLISH, even if user asks in another language.
- User: "Лучшие парки в Париже" → location="Paris" (not "Париж")
- User: "Топ-5 баров в Мюнхене" → location="Munich" (not "Мюнхен")
- User: "Музеи в Лондоне" → location="London" (not "Лондон")

KEYWORD DETECTION FOR COUNT:
- If user says "tour" (e.g., "museum tour", "park tour") → count should be at least 3-5 places
- If user says "best" without a number → count=3 (default)
- If user specifies a number explicitly → use that EXACT number (even if it's 20, 40, 50, etc.)
- IMPORTANT: Don't limit the count - extract the exact number the user requested

If user's request is a FOLLOW-UP, REFINEMENT, or MODIFICATION:
- Use BOTH previous request AND previous response to understand full context
- COUNT the number of places in the previous response (look for numbered list 1., 2., 3., etc.)
- Examples of modifications:
  * "replace 4th bar with something closer to center" - knows which bar is 4th from previous response
  * "can you choose 3 parks for 2 hours?" - refines count from previous request
  * "make it closer to center" - modifies location preference
  * "remove last" / "delete last" / "удали последний" → count should be (previous_count - 1)
  * "remove 2 places" / "удали 2 места" → count should be (previous_count - 2)
  * "add one more" / "добавь ещё один" / "добавь ещё бар" → count should be (previous_count + 1)
  * "add 2 more bars" / "добавь ещё 2 бара" → count should be (previous_count + 2)

IMPORTANT: For ADD/REMOVE operations:
1. FIRST count how many numbered items (1., 2., 3., ...) are in previous_response
2. If "remove" → new_count = previous_count - N
3. If "add" → new_count = previous_count + N
4. Return the calculated count

Examples:
- "Top 5 bars in Munich" → is_route_request=true, location="Munich", place_type="bars", count=5
- "3 modern art museums in Berlin walking" → is_route_request=true, location="Berlin", place_type="museums", count=3, theme="modern art", travel_mode="walking"
- "How's the weather?" → is_route_request=false

Always be helpful and extract as much structure as possible.""",
            }
        ]

        # Add previous conversation for context if available
        if previous_request and previous_response:
            messages.extend(
                [
                    {"role": "user", "content": previous_request},
                    {
                        "role": "assistant",
                        "content": previous_response[:500],
                    },  # Truncate to save tokens
                    {"role": "user", "content": user_message},
                ]
            )
        elif previous_request:
            messages.extend(
                [
                    {"role": "user", "content": previous_request},
                    {"role": "assistant", "content": "I understand your request for places."},
                    {"role": "user", "content": user_message},
                ]
            )
        else:
            messages.append({"role": "user", "content": user_message})

        try:
            response = await self.async_client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=messages,
                response_format=QueryClassification,
            )

            classification = response.choices[0].message.parsed

            logger.info(
                "query_classified",
                is_route_request=classification.is_route_request,
                location=classification.location,
                place_type=classification.place_type,
                count=classification.count,
            )

            return classification

        except Exception as e:
            logger.error("query_classification_failed", error=str(e))
            raise

    async def suggest_places(
        self,
        location: str,
        place_type: str,
        count: int,
        theme: str | None = None,
        previous_places: list | None = None,
        modification_request: str | None = None,
        operation_hint: str | None = None,
        excluded_places: list | None = None,
    ) -> PlaceSuggestions:
        """
        Generate intelligent place suggestions using AI

        Args:
            location: City or area name
            place_type: Type of places (bars, museums, parks, etc)
            count: Number of places to suggest
            theme: Optional theme or preference
            previous_places: Previous list of places (for modifications)
            modification_request: What to modify (e.g., "remove last", "replace 4th")

        Returns:
            PlaceSuggestions with list of places and route description

        Raises:
            ValueError: If OpenAI is not configured
        """
        if not self.is_available():
            raise ValueError("OpenAI service is not configured")

        logger.debug(
            "suggesting_places",
            location=location,
            place_type=place_type,
            count=count,
            theme=theme,
            has_previous=previous_places is not None,
            operation_hint=operation_hint,
        )

        # Build prompt based on whether this is a modification
        if previous_places and modification_request:
            # Modification mode
            places_list = "\n".join([f"{i + 1}. {p}" for i, p in enumerate(previous_places)])
            theme_text = f" focusing on {theme}" if theme else ""
            prompt = f"""MODIFICATION REQUEST: {modification_request}

CURRENT LIST of {place_type} in {location}:
{places_list}

USER WANTS TO: {modification_request}

USER IS DOING: {f"**{operation_hint.upper()}**" if operation_hint else "UNKNOWN"} operation

INSTRUCTIONS:
- Understand what the user wants to change (remove, replace, add, etc.)

REMOVE operations:
- If "remove last" / "delete last" / "удали последний" → KEEP ALL ITEMS EXCEPT THE LAST ONE
- If "remove first" → KEEP ALL ITEMS EXCEPT THE FIRST ONE
- Just copy items from current list, excluding the one(s) to remove
- Example: User has [A, B, C, D, E] and says "remove last" → return [A, B, C, D]

ADD operations:
- If "add" / "добавь ещё" → ADD NEW items to the existing list
- Keep ALL existing items UNCHANGED (SAME EXACT NAMES!)
- Add NEW items that fit the criteria
- Example: User has [A, B, C, D] and says "add one more in center" → return [A, B, C, D, NEW_E]

REPLACE operations:
- **REPLACE_LAST**: "последний далеко" / "last one is far" → replace ONLY the LAST item with a NEW one
  * Keep items 1 to N-1 EXACTLY as they were
  * Replace ONLY item N with a NEW place
  * Example: [A, B, C] + "last is far" → [A, B, NEW_C]

- **REPLACE_ALL**: "все далеко" / "not center" / "bad selection" → replace ALL items
  * Suggest completely NEW places
  * Example: [A, B, C] + "not center" → [NEW_1, NEW_2, NEW_3]

Examples of REPLACE_LAST:
- User: "последний далеко" → Keep first N-1 items, replace only last one
- User: "этот бар слишком далеко" → Keep others, replace the mentioned one

Examples of REPLACE_ALL:
- User: "это не центр блять" → Replace ALL with places in city center (Marienplatz area)
- User: "все плохие" → Replace ALL with better options

CRITICAL:
- For ADD/REMOVE: Keep unchanged items EXACTLY (SAME NAMES!)
- For REPLACE_LAST: Keep all except last with EXACT SAME NAMES, replace only last
- For REPLACE_ALL: Suggest completely NEW items
- **CITY CENTER** for Munich = Marienplatz, Altstadt area (NOT Giesinger, NOT suburbs!)

Return the final list with {count} places total."""
        else:
            # New request mode
            theme_text = f" focusing on {theme}" if theme else ""

            # Add excluded places if this is a retry attempt
            excluded_text = ""
            if excluded_places:
                excluded_list = "\n".join([f"- {p}" for p in excluded_places])
                excluded_text = f"""
DO NOT suggest these places (already checked, not found or wrong city):
{excluded_list}

Suggest DIFFERENT places that actually exist in {location}.
"""

            prompt = f"""Suggest {count} best {place_type} in {location}{theme_text}.

{excluded_text}

CRITICAL REQUIREMENTS:
1. ALL places MUST be physically located WITHIN the city limits of {location}
2. Do NOT suggest places from neighboring cities, suburbs, or regions
3. Use REAL, SPECIFIC place names that actually exist (not generic names)
4. Use well-known, popular places that can be easily found on Google Maps
5. Include the full proper name as it appears on Google Maps
6. Prioritize FAMOUS, WELL-ESTABLISHED venues over obscure or new places
7. Double-check each place REALLY exists in {location} before suggesting

EXAMPLES OF WHAT NOT TO DO:
- User asks for Munich → DON'T suggest places from Stuttgart, Augsburg, or other cities
- User asks for London → DON'T suggest places from Brighton, Oxford, or suburbs
- DON'T make up place names that don't exist
- DON'T suggest vague names like "The Irish Pub" - use FULL NAME like "Kilians Irish Pub München"

For each place provide:
- Name: The exact, full name as it appears in Google Maps
- Short description: 1-2 sentences about what makes it special
- Why recommended: Brief explanation of why it's a good choice

Also provide:
- Overall route description (how these places connect thematically)
- Estimated duration for visiting all places

CRITICAL: Before suggesting any place, verify it is INSIDE the city of {location}.
If you're not 100% sure a place is in {location}, DO NOT suggest it."""

        try:
            response = await self.async_client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a knowledgeable local guide with deep knowledge of specific cities and their venues.

STRICT RULES:
1. Only suggest places that are PHYSICALLY LOCATED in the requested city
2. Never suggest places from nearby cities, suburbs, or regions
3. Use EXACT names as they appear on Google Maps
4. Only suggest well-known, established venues that definitely exist
5. Prioritize popular, easily findable places over obscure ones

Example BAD suggestions:
- Suggesting a place from a different city
- Using generic names like "Central Bar" or "Downtown Museum"
- Suggesting temporary venues or events

Example GOOD suggestions:
- "Hofbräuhaus München" (specific, famous, in Munich)
- "Alte Pinakothek" (exact Google Maps name, established, in Munich)""",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format=PlaceSuggestions,
            )

            suggestions = response.choices[0].message.parsed

            logger.info("places_suggested", count=len(suggestions.places), location=location)

            return suggestions

        except Exception as e:
            logger.error("place_suggestion_failed", error=str(e))
            raise

    def suggest_places_sync(
        self, location: str, place_type: str, count: int, theme: str | None = None
    ) -> PlaceSuggestions:
        """
        Synchronous version of suggest_places (for non-async contexts)

        Args:
            location: City or area name
            place_type: Type of places
            count: Number of places
            theme: Optional theme

        Returns:
            PlaceSuggestions with list of places
        """
        if not self.is_available():
            raise ValueError("OpenAI service is not configured")

        theme_text = f" focusing on {theme}" if theme else ""
        prompt = f"""Suggest {count} best {place_type} in {location}{theme_text}.

For each place provide: name, short description, and why it's recommended.
Also provide overall route description and estimated duration."""

        try:
            response = self.client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a knowledgeable local guide. Suggest REAL, specific place names.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format=PlaceSuggestions,
            )

            return response.choices[0].message.parsed

        except Exception as e:
            logger.error("place_suggestion_failed_sync", error=str(e))
            raise

    async def route_request(
        self,
        current_message: str,
        previous_request: str | None = None,
        previous_response: str | None = None,
        previous_places_count: int = 0,
    ) -> AgentRoutingDecision:
        """
        Agent-based routing decision

        Instead of keyword detection, ask AI to analyze context and decide routing.
        This makes the system easily extensible - just add new questions to the prompt.

        Args:
            current_message: Current user message
            previous_request: Previous user request (if any)
            previous_response: Previous AI response (if any)
            previous_places_count: Number of places in previous response

        Returns:
            AgentRoutingDecision with routing strategy

        Raises:
            ValueError: If OpenAI is not configured
        """
        if not self.is_available():
            raise ValueError("OpenAI service is not configured")

        logger.debug(
            "agent_routing_started",
            current_message=current_message[:100],
            has_previous=bool(previous_request),
        )

        try:
            # Build context
            context_messages = [
                {
                    "role": "system",
                    "content": """You are a routing agent that analyzes user requests and decides how to handle them.

Your task is to determine:
1. Is this a NEW request or a MODIFICATION of the previous request?
2. If modification, what type: add / remove / replace_last / replace_all / refine?
3. Should we use previous places as context?

Guidelines:
- NEW REQUEST: If location OR place_type changed significantly
  * Example: "parks in Paris" → "bars in Munich" = NEW

- MODIFICATION types:
  * ADD: User wants to add MORE places ("add 2 more", "one more bar")
  * REMOVE: User wants to remove places ("delete last", "remove 2")
  * REPLACE_LAST: User criticizes ONLY the last place ("last one is far", "change last bar")
  * REPLACE_ALL: User criticizes the whole selection ("not in center", "too far", "bad")
  * REFINE: User adjusts parameters but keeps same places ("make it 2 hours instead")

Context analysis:
- If previous_request is about Paris parks and current is about Munich bars → NEW REQUEST
- If previous_request is about Munich bars and current is "add one more" → MODIFICATION (ADD)
- If current message doesn't mention location/place_type, it's likely a MODIFICATION

Be smart about context and provide reasoning for debugging.""",
                }
            ]

            # Add previous context if available
            if previous_request and previous_response:
                context_messages.append(
                    {"role": "user", "content": f"PREVIOUS REQUEST: {previous_request}"}
                )
                context_messages.append(
                    {
                        "role": "assistant",
                        "content": f"PREVIOUS RESPONSE: {previous_response[:500]}...",  # Truncate for token efficiency
                    }
                )
                context_messages.append(
                    {
                        "role": "system",
                        "content": f"Previous response contained {previous_places_count} places.",
                    }
                )

            # Current message
            context_messages.append(
                {
                    "role": "user",
                    "content": f"CURRENT REQUEST: {current_message}\n\nAnalyze and decide routing.",
                }
            )

            response = await self.async_client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=context_messages,
                response_format=AgentRoutingDecision,
            )

            routing = response.choices[0].message.parsed

            logger.info(
                "agent_routing_decided",
                is_new=routing.is_new_request,
                operation=routing.operation_type,
                use_context=routing.use_previous_context,
                reasoning=routing.reasoning,
            )

            return routing

        except Exception as e:
            logger.error("agent_routing_failed", error=str(e))
            raise
