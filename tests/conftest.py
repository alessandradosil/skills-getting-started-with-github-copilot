"""Pytest configuration and fixtures for the Activities API tests"""
import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


# Store the original activities data for reset between tests
ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture
def client():
    """Provide a TestClient instance for testing the API"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state before each test
    
    This fixture ensures test isolation by resetting the in-memory
    activities database to its original state before each test runs.
    """
    # Reset activities to original state
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))
    yield
    # Cleanup after test (optional, but good practice)
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))
