import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    """Test that root endpoint redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    """Test getting the list of activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0
    
    # Test structure of an activity
    activity = next(iter(activities.values()))
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)

def test_signup_for_activity():
    """Test signing up for an activity"""
    # Get first activity name
    response = client.get("/activities")
    activities = response.json()
    activity_name = next(iter(activities.keys()))
    
    # Test successful signup
    test_email = "test_student@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {test_email} for {activity_name}"
    
    # Verify student is in participants list
    response = client.get("/activities")
    assert test_email in response.json()[activity_name]["participants"]
    
    # Test duplicate signup
    response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()

def test_unregister_from_activity():
    """Test unregistering from an activity"""
    # First sign up a test student
    response = client.get("/activities")
    activities = response.json()
    activity_name = next(iter(activities.keys()))
    test_email = "test_unregister@mergington.edu"
    
    # Sign up the student first
    client.post(f"/activities/{activity_name}/signup?email={test_email}")
    
    # Test successful unregistration
    response = client.post(f"/activities/{activity_name}/unregister?email={test_email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {test_email} from {activity_name}"
    
    # Verify student is removed from participants list
    response = client.get("/activities")
    assert test_email not in response.json()[activity_name]["participants"]
    
    # Test unregistering non-registered student
    response = client.post(f"/activities/{activity_name}/unregister?email={test_email}")
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"].lower()

def test_activity_not_found():
    """Test error handling for non-existent activities"""
    fake_activity = "Fake Activity"
    test_email = "test@mergington.edu"
    
    # Test signup for non-existent activity
    response = client.post(f"/activities/{fake_activity}/signup?email={test_email}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
    
    # Test unregister from non-existent activity
    response = client.post(f"/activities/{fake_activity}/unregister?email={test_email}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()