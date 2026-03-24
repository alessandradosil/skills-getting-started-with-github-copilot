"""Integration and scenario tests for the Activities API"""
import pytest


class TestSignupWorkflow:
    """Tests for complete signup workflows"""
    
    def test_full_signup_workflow(self, client):
        """Test complete workflow: signup -> verify -> delete -> verify"""
        email = "testuser@mergington.edu"
        activity = "Programming Class"
        
        # Step 1: Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Step 2: Verify student is in list
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Step 3: Delete registration
        response = client.delete(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Step 4: Verify student is no longer in list
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]
    
    def test_signup_multiple_different_activities(self, client):
        """Test student can sign up for multiple different activities"""
        email = "multiactivity@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Sign up for each activity
        for activity in activities_to_join:
            response = client.post(
                f"/activities/{activity}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify student is in all activities
        response = client.get("/activities")
        activities_data = response.json()
        for activity in activities_to_join:
            assert email in activities_data[activity]["participants"]
    
    def test_signup_delete_then_resignup_different_activity(self, client):
        """Test signup, delete from one activity, then signup for different activity"""
        email = "flexible@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Science Olympiad"
        
        # Sign up for activity 1
        client.post(f"/activities/{activity1}/signup?email={email}")
        response = client.get("/activities")
        assert email in response.json()[activity1]["participants"]
        
        # Delete from activity 1
        client.delete(f"/activities/{activity1}/signup?email={email}")
        response = client.get("/activities")
        assert email not in response.json()[activity1]["participants"]
        
        # Sign up for activity 2
        client.post(f"/activities/{activity2}/signup?email={email}")
        response = client.get("/activities")
        assert email in response.json()[activity2]["participants"]
        assert email not in response.json()[activity1]["participants"]


class TestMultipleStudents:
    """Tests for multiple students interacting with activities"""
    
    def test_multiple_students_same_activity(self, client):
        """Test multiple different students signing up for same activity"""
        activity = "Debate Club"
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu",
            "student4@mergington.edu",
        ]
        
        for email in emails:
            response = client.post(
                f"/activities/{activity}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all students are in list
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        for email in emails:
            assert email in participants
        
        # Verify count is correct (existing + new)
        expected_count = 1 + len(emails)  # Debate Club has 1 existing
        assert len(participants) == expected_count
    
    def test_partial_unregister_from_shared_activity(self, client):
        """Test unregistering one student doesn't affect others"""
        activity = "Basketball Team"
        email_to_remove = "alex@mergington.edu"  # Currently registered
        other_email = "newstudent@mergington.edu"
        
        # Add new student
        client.post(f"/activities/{activity}/signup?email={other_email}")
        
        # Verify both are registered
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert email_to_remove in participants
        assert other_email in participants
        
        # Remove one student
        client.delete(f"/activities/{activity}/signup?email={email_to_remove}")
        
        # Verify only the other student remains
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert email_to_remove not in participants
        assert other_email in participants


class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""
    
    def test_case_sensitivity_in_activity_names(self, client):
        """Test how different case variations of activity names are handled"""
        email = "student@mergington.edu"
        
        # Try lowercase version of an activity
        response = client.post(
            f"/activities/chess%20club/signup?email={email}"
        )
        # Should fail because exact case match is required
        assert response.status_code == 404
        
        # Correct case should work
        response = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response.status_code == 200
    
    def test_activity_name_with_spaces(self, client):
        """Test that activity names with spaces are handled correctly"""
        email = "student@mergington.edu"
        activity = "Programming Class"  # Has a space
        
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response.status_code == 200
    
    def test_special_characters_in_email(self, client):
        """Test email addresses with special characters"""
        activity = "Gym Class"
        special_emails = [
            "student+tag@mergington.edu",
            "first.last@mergington.edu",
            "student_123@mergington.edu",
        ]
        
        for email in special_emails:
            response = client.post(
                f"/activities/{activity}/signup?email={email}"
            )
            assert response.status_code == 200
    
    def test_same_email_format_variations_are_different(self, client):
        """Test that email address variations are treated as different students"""
        activity = "Art Studio"
        email1 = "student@mergington.edu"
        email2 = "student.different@mergington.edu"
        
        # Both should be able to sign up (they're different emails)
        response1 = client.post(
            f"/activities/{activity}/signup?email={email1}"
        )
        response2 = client.post(
            f"/activities/{activity}/signup?email={email2}"
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Both should be in the participant list
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert email1 in participants
        assert email2 in participants


class TestResponseConsistency:
    """Tests for response format consistency"""
    
    def test_signup_response_format(self, client):
        """Test that signup response has correct format"""
        email = "student@mergington.edu"
        activity = "Soccer Club"
        
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], str)
    
    def test_delete_response_format(self, client):
        """Test that delete response has correct format"""
        email = "james@mergington.edu"  # Currently in Soccer Club
        activity = "Soccer Club"
        
        response = client.delete(
            f"/activities/{activity}/signup?email={email}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], str)
    
    def test_error_response_format(self, client):
        """Test that error responses have correct format"""
        email = "student@mergington.edu"
        activity = "Nonexistent"
        
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
