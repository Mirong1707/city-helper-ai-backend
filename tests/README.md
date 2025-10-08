# Testing Guide

## Overview

This project uses pytest for testing with a focus on **agent-based routing** integration tests.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                          # Shared fixtures
├── integration/
│   ├── __init__.py
│   └── test_agent_routing.py           # Agent routing decision tests
└── README.md                            # This file
```

## Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.openai` - Tests that make real OpenAI API calls
- `@pytest.mark.integration` - Integration tests with external services
- `@pytest.mark.unit` - Fast unit tests with mocked dependencies
- `@pytest.mark.slow` - Tests that take >1 second

## Running Tests

### Quick Commands

```bash
# Run only unit tests (fast, no API calls)
make test-unit

# Run integration tests (includes OpenAI API calls ~$0.03)
make test-integration

# Run all tests
make test-all

# Run with coverage report
make test-coverage
```

### Detailed Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run only integration tests
pytest tests/integration/ -v

# Skip OpenAI tests (for CI)
pytest tests/ -v -m "not openai"

# Run only OpenAI tests
pytest tests/ -v -m "openai"

# Run specific test class
pytest tests/integration/test_agent_routing.py::TestAgentRoutingNewRequest -v

# Run specific test
pytest tests/integration/test_agent_routing.py::TestAgentRoutingNewRequest::test_new_request_different_city_and_type -v

# Show stdout/stderr during tests
pytest tests/ -v -s

# Stop on first failure
pytest tests/ -x

# Run last failed tests only
pytest tests/ --lf
```

## Agent Routing Tests

Integration tests for agent-based routing verify the decision tree documented in `AGENT_ROUTING_BLUEPRINT.md`.

### Test Coverage Matrix

| Test Class | Tests | Coverage |
|------------|-------|----------|
| `TestAgentRoutingNewRequest` | 2 | NEW REQUEST detection |
| `TestAgentRoutingModifications` | 7 | ADD, REMOVE, REPLACE_LAST, REPLACE_ALL, REFINE |
| `TestAgentRoutingEdgeCases` | 2 | No context, ambiguous inputs |
| `TestAgentRoutingReasoning` | 1 | Reasoning quality |

### Example Test Run

```bash
$ pytest tests/integration/test_agent_routing.py -v

tests/integration/test_agent_routing.py::TestAgentRoutingNewRequest::test_new_request_different_city_and_type PASSED [ 8%]
tests/integration/test_agent_routing.py::TestAgentRoutingNewRequest::test_new_request_different_city_same_type PASSED [ 16%]
tests/integration/test_agent_routing.py::TestAgentRoutingModifications::test_add_operation_explicit PASSED [ 25%]
tests/integration/test_agent_routing.py::TestAgentRoutingModifications::test_add_operation_implicit PASSED [ 33%]
tests/integration/test_agent_routing.py::TestAgentRoutingModifications::test_remove_operation_last PASSED [ 41%]
tests/integration/test_agent_routing.py::TestAgentRoutingModifications::test_replace_last_operation PASSED [ 50%]
tests/integration/test_agent_routing.py::TestAgentRoutingModifications::test_replace_all_operation_not_in_center PASSED [ 58%]
tests/integration/test_agent_routing.py::TestAgentRoutingModifications::test_replace_all_operation_too_far PASSED [ 66%]
tests/integration/test_agent_routing.py::TestAgentRoutingModifications::test_refine_operation_adjust_count PASSED [ 75%]
tests/integration/test_agent_routing.py::TestAgentRoutingEdgeCases::test_no_previous_context PASSED [ 83%]
tests/integration/test_agent_routing.py::TestAgentRoutingEdgeCases::test_ambiguous_same_city_add_or_replace PASSED [ 91%]
tests/integration/test_agent_routing.py::TestAgentRoutingReasoning::test_reasoning_contains_explanation PASSED [100%]

============================== 12 passed in 38.52s ===============================
```

**Cost:** ~$0.03 USD for full suite

## Cost Estimation

Using `gpt-4o-mini` for routing decisions:

- **Single test:** ~$0.0003 (0.03 cents)
- **Full suite (12 tests):** ~$0.036 (3.6 cents)
- **Monthly CI runs (30 runs):** ~$1.08

Negligible cost for the value provided.

## CI/CD Integration

For CI pipelines where OpenAI API calls should be skipped:

```yaml
# .github/workflows/test.yml
- name: Run tests (skip OpenAI)
  run: pytest tests/ -v -m "not openai"
```

For manual/scheduled test runs with OpenAI:

```yaml
# .github/workflows/integration-test.yml (manual trigger)
- name: Run integration tests
  run: pytest tests/ -v -m "openai"
  env:
    SECRET_OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

## Fixtures

Available fixtures (defined in `conftest.py`):

- `openai_service` - OpenAIService instance (session scope)
- `mock_previous_response_bars` - Mock response with 5 bars
- `mock_previous_response_parks` - Mock response with 3 parks
- `mock_previous_request_bars` - Mock request "Top 5 bars in Munich"
- `mock_previous_request_parks` - Mock request "Best parks in Paris"

## Adding New Tests

1. **Update Blueprint** - Add new operation to `AGENT_ROUTING_BLUEPRINT.md`
2. **Update Schema** - Add operation type to `app/schemas/agent.py`
3. **Update Prompt** - Add operation description to `app/services/openai_service.py`
4. **Write Test** - Add test case to `test_agent_routing.py`
5. **Run Test** - Verify with `pytest`

### Test Template

```python
@pytest.mark.asyncio
@pytest.mark.openai
async def test_your_scenario(self, openai_service, mock_previous_request_bars, mock_previous_response_bars):
    """
    Scenario: Description
    Expected: Expected routing decision
    Blueprint: Path through decision tree
    """
    routing = await openai_service.route_request(
        current_message="your message",
        previous_request=mock_previous_request_bars,
        previous_response=mock_previous_response_bars,
        previous_places_count=5
    )

    assert routing.operation_type == "expected_type", \
        f"Expected 'expected_type', got: {routing.operation_type}. Reasoning: {routing.reasoning}"
```

## Debugging Tests

### Show full output

```bash
pytest tests/ -v -s --tb=long
```

### Show only failures

```bash
pytest tests/ --tb=short
```

### Run with pdb on failure

```bash
pytest tests/ --pdb
```

### Show reasoning for failed tests

All assertions include `routing.reasoning` in the error message for easy debugging.

## Best Practices

1. **Use descriptive test names** - Test name should describe scenario
2. **Include reasoning in assertions** - Always show `routing.reasoning` on failure
3. **Document expected behavior** - Use docstrings with Scenario/Expected/Blueprint
4. **Keep tests independent** - Don't rely on test execution order
5. **Use fixtures for common data** - Avoid hardcoding test data
6. **Cost-aware** - Mark expensive tests with `@pytest.mark.openai`

## Troubleshooting

### Tests skipped with "OpenAI API key not configured"

Set `SECRET_OPENAI_API_KEY` in your `.env` file:

```bash
echo "SECRET_OPENAI_API_KEY=sk-..." >> .env/.env
```

### Tests fail with import errors

Install test dependencies:

```bash
pip install -r requirements.txt
```

### Tests are slow

Use `pytest-xdist` for parallel execution:

```bash
pip install pytest-xdist
pytest tests/ -n auto
```

Note: OpenAI tests will still be sequential due to API rate limits.
