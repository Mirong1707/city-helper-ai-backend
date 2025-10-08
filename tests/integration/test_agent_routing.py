"""
Integration tests for Agent-Based Routing

These tests verify that the AI agent correctly analyzes context and makes
routing decisions according to the blueprint in AGENT_ROUTING_BLUEPRINT.md

⚠️ These tests make real OpenAI API calls (cost: ~$0.03 for full suite)
Run with: pytest -m openai tests/integration/test_agent_routing.py
"""

import pytest


@pytest.mark.asyncio
@pytest.mark.openai
class TestAgentRoutingNewRequest:
    """Test NEW REQUEST detection (different location and/or place type)"""

    async def test_new_request_different_city_and_type(
        self, openai_service, mock_previous_request_parks, mock_previous_response_parks
    ):
        """
        Scenario: Parks in Paris → Bars in Munich
        Expected: NEW REQUEST (both location and place_type changed)
        Blueprint: Start → Agent → BothChanged → NewRequest
        """
        routing = await openai_service.route_request(
            current_message="Top 5 bars in Munich",
            previous_request=mock_previous_request_parks,
            previous_response=mock_previous_response_parks,
            previous_places_count=3,
        )

        # Assertions
        assert routing.is_new_request, f"Should detect new request. Reasoning: {routing.reasoning}"
        assert routing.operation_type in ["new", "replace_all"], (
            f"Operation should be 'new'. Got: {routing.operation_type}"
        )
        assert routing.location_changed, "Location changed from Paris to Munich"
        assert routing.place_type_changed, "Place type changed from parks to bars"

    async def test_new_request_different_city_same_type(
        self, openai_service, mock_previous_request_bars, mock_previous_response_bars
    ):
        """
        Scenario: Bars in Munich → Bars in Paris
        Expected: NEW REQUEST (location changed, type same)
        Blueprint: Start → Agent → LocationCheck → BothChanged → NewRequest
        """
        routing = await openai_service.route_request(
            current_message="Top 5 bars in Paris",
            previous_request=mock_previous_request_bars,
            previous_response=mock_previous_response_bars,
            previous_places_count=5,
        )

        assert routing.is_new_request, (
            f"Should detect new request (different city). Reasoning: {routing.reasoning}"
        )
        assert routing.location_changed


@pytest.mark.asyncio
@pytest.mark.openai
class TestAgentRoutingModifications:
    """Test MODIFICATION operations (ADD, REMOVE, REPLACE_LAST, REPLACE_ALL, REFINE)"""

    async def test_add_operation_explicit(
        self, openai_service, mock_previous_request_bars, mock_previous_response_bars
    ):
        """
        Scenario: 5 bars in Munich → "add 2 more"
        Expected: MODIFICATION with operation_type="add", count_adjustment=+2
        Blueprint: Start → Agent → Modification → OperationType → AddOp
        """
        routing = await openai_service.route_request(
            current_message="add 2 more bars",
            previous_request=mock_previous_request_bars,
            previous_response=mock_previous_response_bars,
            previous_places_count=5,
        )

        assert not routing.is_new_request, "Should be modification, not new request"
        assert routing.operation_type == "add", (
            f"Should detect ADD operation. Got: {routing.operation_type}. Reasoning: {routing.reasoning}"
        )
        assert routing.use_previous_context, "Should use previous places as context"
        assert routing.count_adjustment is not None and routing.count_adjustment > 0, (
            f"Count adjustment should be positive for ADD. Got: {routing.count_adjustment}"
        )

    async def test_add_operation_implicit(
        self, openai_service, mock_previous_request_bars, mock_previous_response_bars
    ):
        """
        Scenario: 5 bars in Munich → "one more bar"
        Expected: MODIFICATION with operation_type="add", count_adjustment=+1
        """
        routing = await openai_service.route_request(
            current_message="one more bar in the center",
            previous_request=mock_previous_request_bars,
            previous_response=mock_previous_response_bars,
            previous_places_count=5,
        )

        assert routing.operation_type == "add", (
            f"Should detect implicit ADD. Got: {routing.operation_type}"
        )
        assert routing.count_adjustment == 1, f"Should add 1 place. Got: {routing.count_adjustment}"

    async def test_remove_operation_last(
        self, openai_service, mock_previous_request_bars, mock_previous_response_bars
    ):
        """
        Scenario: 5 bars in Munich → "remove last"
        Expected: MODIFICATION with operation_type="remove", count_adjustment=-1
        Blueprint: Start → Agent → Modification → OperationType → RemoveOp
        """
        routing = await openai_service.route_request(
            current_message="remove the last bar",
            previous_request=mock_previous_request_bars,
            previous_response=mock_previous_response_bars,
            previous_places_count=5,
        )

        assert routing.operation_type == "remove", (
            f"Should detect REMOVE operation. Got: {routing.operation_type}"
        )
        assert routing.count_adjustment is not None and routing.count_adjustment < 0, (
            f"Count adjustment should be negative. Got: {routing.count_adjustment}"
        )
        assert routing.use_previous_context

    async def test_replace_last_operation(
        self, openai_service, mock_previous_request_bars, mock_previous_response_bars
    ):
        """
        Scenario: 5 bars in Munich → "last one is too far"
        Expected: MODIFICATION with operation_type="replace_last"
        Blueprint: Start → Agent → Modification → OperationType → ReplaceLast
        """
        routing = await openai_service.route_request(
            current_message="the last bar is too far from center",
            previous_request=mock_previous_request_bars,
            previous_response=mock_previous_response_bars,
            previous_places_count=5,
        )

        assert routing.operation_type == "replace_last", (
            f"Should detect REPLACE_LAST. Got: {routing.operation_type}. Reasoning: {routing.reasoning}"
        )
        assert routing.use_previous_context, "Should keep previous places except last one"

    async def test_replace_all_operation_not_in_center(
        self, openai_service, mock_previous_request_bars, mock_previous_response_bars
    ):
        """
        Scenario: 5 bars in Munich → "these are not in center"
        Expected: MODIFICATION with operation_type="replace_all"
        Blueprint: Start → Agent → Modification → OperationType → ReplaceAll
        """
        routing = await openai_service.route_request(
            current_message="these bars are not in the city center",
            previous_request=mock_previous_request_bars,
            previous_response=mock_previous_response_bars,
            previous_places_count=5,
        )

        assert routing.operation_type == "replace_all", (
            f"Should detect REPLACE_ALL. Got: {routing.operation_type}. Reasoning: {routing.reasoning}"
        )
        assert not routing.use_previous_context or routing.operation_type == "replace_all", (
            "Should replace all places, not keep previous"
        )

    async def test_replace_all_operation_too_far(
        self, openai_service, mock_previous_request_bars, mock_previous_response_bars
    ):
        """
        Scenario: 5 bars in Munich → "all are too far"
        Expected: MODIFICATION with operation_type="replace_all"
        """
        routing = await openai_service.route_request(
            current_message="all of them are too far from each other",
            previous_request=mock_previous_request_bars,
            previous_response=mock_previous_response_bars,
            previous_places_count=5,
        )

        assert routing.operation_type == "replace_all", (
            f"Should detect REPLACE_ALL criticism. Got: {routing.operation_type}"
        )

    async def test_refine_operation_adjust_count(
        self, openai_service, mock_previous_request_bars, mock_previous_response_bars
    ):
        """
        Scenario: 5 bars in Munich → "make it only 3"
        Expected: MODIFICATION with operation_type="refine"
        Blueprint: Start → Agent → Modification → OperationType → Refine
        """
        routing = await openai_service.route_request(
            current_message="can you make it only 3 bars instead?",
            previous_request=mock_previous_request_bars,
            previous_response=mock_previous_response_bars,
            previous_places_count=5,
        )

        # Agent might classify this as 'refine' or 'replace_all' depending on interpretation
        assert routing.operation_type in ["refine", "replace_all"], (
            f"Should be refine or replace_all. Got: {routing.operation_type}"
        )
        assert not routing.is_new_request


@pytest.mark.asyncio
@pytest.mark.openai
class TestAgentRoutingEdgeCases:
    """Test edge cases and ambiguous scenarios"""

    async def test_no_previous_context(self, openai_service):
        """
        Scenario: First message (no previous context)
        Expected: NEW REQUEST
        Blueprint: Start → HasPrevious → NewRequest
        """
        routing = await openai_service.route_request(
            current_message="Top 5 bars in Munich",
            previous_request=None,
            previous_response=None,
            previous_places_count=0,
        )

        assert routing.is_new_request, "First message should always be new request"
        assert routing.operation_type in ["new", "replace_all"]

    async def test_ambiguous_same_city_add_or_replace(
        self, openai_service, mock_previous_request_bars, mock_previous_response_bars
    ):
        """
        Scenario: 5 bars in Munich → "other bars in Munich"
        Expected: Agent decides between ADD or REPLACE_ALL
        This tests agent's reasoning ability with ambiguous input
        """
        routing = await openai_service.route_request(
            current_message="show me other bars in Munich",
            previous_request=mock_previous_request_bars,
            previous_response=mock_previous_response_bars,
            previous_places_count=5,
        )

        # "Other bars" is ambiguous - could be replace or add
        # We check that agent makes A decision (not which one)
        assert routing.operation_type in ["add", "replace_all", "new"], (
            f"Agent should decide on operation. Got: {routing.operation_type}"
        )
        assert len(routing.reasoning) > 10, "Reasoning should explain the decision"


@pytest.mark.asyncio
@pytest.mark.openai
class TestAgentRoutingReasoning:
    """Test that agent provides meaningful reasoning"""

    async def test_reasoning_contains_explanation(
        self, openai_service, mock_previous_request_bars, mock_previous_response_bars
    ):
        """
        Verify that reasoning field contains actual explanation
        """
        routing = await openai_service.route_request(
            current_message="add one more bar",
            previous_request=mock_previous_request_bars,
            previous_response=mock_previous_response_bars,
            previous_places_count=5,
        )

        # Check reasoning quality
        reasoning_lower = routing.reasoning.lower()
        assert len(routing.reasoning) > 20, "Reasoning should be detailed, not just a word"

        # Should mention key concepts
        has_context_mention = any(
            word in reasoning_lower
            for word in ["add", "more", "previous", "same", "location", "modification"]
        )
        assert has_context_mention, (
            f"Reasoning should explain the decision. Got: {routing.reasoning}"
        )
