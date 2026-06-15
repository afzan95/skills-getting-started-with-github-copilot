"""
Pytest configuration and fixtures for FastAPI tests.

This module provides a TestClient fixture that connects to the FastAPI app
and ensures clean test state between test runs.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to Python path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """
    Provide a TestClient for making HTTP requests to the FastAPI app.
    
    This fixture resets the activities data to a known state before each test
    to ensure test isolation.
    """
    # Reset activities to a clean state for each test
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Competitive soccer practices and matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 22,
            "participants": ["liam@mergington.edu", "noah@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Pick-up games and skill training",
            "schedule": "Wednesdays and Fridays, 4:30 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["ava@mergington.edu", "will@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore drawing, painting, and mixed media",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["mia@mergington.edu", "lucas@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting, stagecraft, and school productions",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["sophia@mergington.edu", "ethan@mergington.edu"]
        },
        "Debate Team": {
            "description": "Competitive debate practice and tournaments",
            "schedule": "Mondays and Wednesdays, 5:00 PM - 6:30 PM",
            "max_participants": 16,
            "participants": ["oliver@mergington.edu", "isabella@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Hands-on science competitions and club meetings",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["mia@mergington.edu", "liam@mergington.edu"]
        }
    })
    
    return TestClient(app)
