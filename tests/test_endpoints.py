"""Tests for core API endpoints"""
import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_success(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        
        assert response.status_code == 200
        activities = response.json()
        
        # Verify all 9 activities are returned
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
        
    def test_get_activities_has_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity in activities.items():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            
    def test_get_activities_participant_list_is_list(self, client):
        """Test that participants is a list for each activity"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity in activities.items():
            assert isinstance(activity["participants"], list)
            
    def test_get_activities_contains_expected_activities(self, client):
        """Test that specific expected activities are returned"""
        response = client.get("/activities")
        activities = response.json()
        
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Soccer Club",
            "Debate Club",
            "Science Olympiad",
            "Art Studio",
            "Drama Club",
        ]
        
        for activity_name in expected_activities:
            assert activity_name in activities


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        assert response.status_code == 200
        assert "message" in response.json()
        assert email in response.json()["message"]
        
    def test_signup_adds_to_participants(self, client):
        """Test that signup adds student to participants list"""
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        # Verify student is not in list initially
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities[activity]["participants"]
        
        # Sign up
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Verify student is now in list
        response = client.get("/activities")
        activities = response.json()
        assert email in activities[activity]["participants"]
        
    def test_signup_activity_not_found(self, client):
        """Test signup returns 404 for non-existent activity"""
        email = "student@mergington.edu"
        activity = "Nonexistent Club"
        
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
        
    def test_signup_already_registered(self, client):
        """Test signup returns 400 when student already registered"""
        email = "michael@mergington.edu"  # Already registered for Chess Club
        activity = "Chess Club"
        
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
        
    @pytest.mark.parametrize("email", [
        "student1@mergington.edu",
        "john.doe@mergington.edu",
        "alice_123@mergington.edu",
        "test+tag@mergington.edu",
    ])
    def test_signup_various_email_formats(self, client, email):
        """Test signup with various valid email formats"""
        activity = "Programming Class"
        
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        assert response.status_code == 200
        
    def test_signup_multiple_students_same_activity(self, client):
        """Test multiple students can sign up for same activity"""
        activity = "Debate Club"
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        for email in emails:
            response = client.post(
                f"/activities/{activity}/signup?email={email}"
            )
            assert response.status_code == 200
            
        # Verify all students are in participants
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        for email in emails:
            assert email in participants
            
    def test_signup_increments_participant_count(self, client):
        """Test that signup increments the participant count"""
        activity = "Art Studio"
        
        # Get initial participant count
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])
        
        # Sign up new student
        email = "newstudent@mergington.edu"
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Verify count increased
        response = client.get("/activities")
        new_count = len(response.json()[activity]["participants"])
        assert new_count == initial_count + 1


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_delete_success(self, client):
        """Test successful unregistration from an activity"""
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"
        
        response = client.delete(
            f"/activities/{activity}/signup?email={email}"
        )
        
        assert response.status_code == 200
        assert "message" in response.json()
        assert email in response.json()["message"]
        
    def test_delete_removes_from_participants(self, client):
        """Test that delete removes student from participants list"""
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Verify student is in list initially
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Delete registration
        client.delete(f"/activities/{activity}/signup?email={email}")
        
        # Verify student is no longer in list
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]
        
    def test_delete_activity_not_found(self, client):
        """Test delete returns 404 for non-existent activity"""
        email = "student@mergington.edu"
        activity = "Nonexistent Club"
        
        response = client.delete(
            f"/activities/{activity}/signup?email={email}"
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
        
    def test_delete_not_registered(self, client):
        """Test delete returns 400 when student not registered"""
        email = "notregistered@mergington.edu"
        activity = "Chess Club"
        
        response = client.delete(
            f"/activities/{activity}/signup?email={email}"
        )
        
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()
        
    def test_delete_decrements_participant_count(self, client):
        """Test that delete decrements the participant count"""
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Get initial participant count
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])
        
        # Delete registration
        client.delete(f"/activities/{activity}/signup?email={email}")
        
        # Verify count decreased
        response = client.get("/activities")
        new_count = len(response.json()[activity]["participants"])
        assert new_count == initial_count - 1
        
    def test_delete_then_can_resignup(self, client):
        """Test that student can re-signup after deletion"""
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Delete registration
        response = client.delete(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Verify student is not in list
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]
        
        # Re-signup should succeed
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Verify student is back in list
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]


class TestRoot:
    """Tests for GET / endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root path redirects to static HTML"""
        response = client.get("/", follow_redirects=False)
        
        # FastAPI redirects are typically 307 (Temporary Redirect)
        assert response.status_code in [307, 308]
        assert "/static/index.html" in response.headers.get("location", "")
