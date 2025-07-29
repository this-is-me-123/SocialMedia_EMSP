# Social Media Automation - Test Suite

This directory contains the test suite for the Social Media Automation System. The tests are organized into unit tests and integration tests, with mocks for external services.

## Test Structure

- `unit/`: Unit tests for individual components
  - `test_health.py`: Health check endpoint tests
  - `test_backup_restore.py`: Backup and restore functionality tests
  - `test_social_media_manager.py`: Social media manager tests
  - `test_*.py`: Other unit tests

- `integration/`: End-to-end integration tests
  - `test_end_to_end.py`: Full system workflow tests
  - `conftest.py`: Test fixtures and configurations

- `mocks/`: Mock implementations for testing
  - `mock_platforms.py`: Mock social media platform implementations

- `fixtures/`: Test data files
- `test_data/`: Generated test data

## Running Tests

### Prerequisites

- Python 3.8+
- Dependencies in `requirements-dev.txt`

### Running All Tests

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests with coverage
pytest --cov=automation_stack --cov=scripts tests/
```

### Running Specific Tests

```bash
# Run unit tests only
pytest tests/unit/

# Run integration tests only
pytest tests/integration/

# Run a specific test file
pytest tests/unit/test_health.py

# Run a specific test case
pytest tests/unit/test_health.py::TestHealthCheck::test_health_endpoint
```

### Test Coverage

To generate a coverage report:

```bash
pytest --cov=automation_stack --cov-report=html tests/
open htmlcov/index.html  # View coverage report
```

## Writing Tests

### Unit Tests

Unit tests should:
- Test a single function or class in isolation
- Use mocks for external dependencies
- Be fast and deterministic
- Have clear, descriptive test names

Example:
```python
def test_schedule_post(manager):
    """Test scheduling a new post."""
    post_id = manager.schedule_post(
        platform="instagram",
        content="Test post",
        scheduled_time="2023-01-01T12:00:00Z"
    )
    assert post_id is not None
```

### Integration Tests

Integration tests should:
- Test interactions between components
- Use real dependencies when possible
- Test complete workflows
- Be isolated from other tests

Example:
```python
def test_post_workflow(manager):
    """Test the complete post creation workflow."""
    # Schedule a post
    post_id = manager.schedule_post(
        platform="instagram",
        content="Test post",
        scheduled_time=(datetime.utcnow() - timedelta(minutes=1)).isoformat()
    )
    
    # Process scheduled posts
    processed = manager.process_scheduled_posts()
    assert processed == 1
    
    # Verify post was created
    post = manager.get_post(post_id)
    assert post["status"] == "posted"
```

## Mocking External Services

Use the mock implementations in `tests/mocks/` to simulate external services:

```python
from tests.mocks.mock_platforms import MockInstagramPlatform

def test_instagram_post():
    platform = MockInstagramPlatform()
    platform.authenticate()
    result = platform.post("Test post", media_urls=["test.jpg"])
    assert result["status"] == "success"
```

## Test Data

- Store static test data in `tests/fixtures/`
- Generate dynamic test data in `tests/test_data/`
- Clean up test data in test teardown

## Best Practices

1. **Isolation**: Each test should be independent
2. **Determinism**: Tests should produce the same results every time
3. **Readability**: Clear test names and assertions
4. **Coverage**: Aim for high test coverage
5. **Speed**: Keep tests fast by mocking expensive operations

## Debugging Tests

To debug a failing test:

```bash
# Run with pdb on failure
pytest --pdb tests/

# Print detailed logs
pytest -v -s tests/
```

## Continuous Integration

Tests are automatically run on push and pull requests via GitHub Actions. See `.github/workflows/ci-cd.yml` for details.
