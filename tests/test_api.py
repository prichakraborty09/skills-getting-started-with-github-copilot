"""
Tests for Mergington High School Activities API

Using the AAA (Arrange-Act-Assert) pattern for test structure:
- Arrange: Set up test data and initial state
- Act: Perform the action being tested
- Assert: Verify the results
"""

from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestGetActivities:
    """Test suite for GET /activities endpoint"""

    def test_get_all_activities_returns_success(self):
        """Arrange: N/A
           Act: Fetch all activities
           Assert: Verify response status and contains activity data
        """
        # Arrange
        # N/A

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        assert "Chess Club" in activities


    def test_get_activities_contains_required_fields(self):
        """Arrange: N/A
           Act: Fetch activities
           Assert: Verify each activity has required fields
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert all(field in activity_data for field in required_fields)
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant_succeeds(self):
        """Arrange: Test email not yet signed up for activity
           Act: Sign up new participant
           Assert: Verify success response
        """
        # Arrange
        test_email = "newstudent@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "Signed up" in result["message"]
        assert test_email in result["message"]


    def test_signup_duplicate_participant_fails(self):
        """Arrange: Student already signed up for activity
           Act: Attempt to sign up same student again
           Assert: Verify 400 error response
        """
        # Arrange
        test_email = "duplicate@mergington.edu"
        activity_name = "Gym Class"
        client.post(f"/activities/{activity_name}/signup", params={"email": test_email})

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )

        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "already signed up" in result["detail"]


    def test_signup_nonexistent_activity_fails(self):
        """Arrange: Activity does not exist
           Act: Attempt to sign up for nonexistent activity
           Assert: Verify 404 error response
        """
        # Arrange
        test_email = "student@mergington.edu"
        nonexistent_activity = "Nonexistent Club"

        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": test_email}
        )

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"].lower()


class TestRemoveParticipant:
    """Test suite for DELETE /activities/{activity_name}/participants/{email} endpoint"""

    def test_remove_existing_participant_succeeds(self):
        """Arrange: Participant exists in activity
           Act: Remove participant from activity
           Assert: Verify success response
        """
        # Arrange
        test_email = "removestudent@mergington.edu"
        activity_name = "Basketball Team"
        client.post(f"/activities/{activity_name}/signup", params={"email": test_email})

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{test_email}"
        )

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "Removed" in result["message"]
        assert test_email in result["message"]


    def test_remove_nonexistent_participant_fails(self):
        """Arrange: Participant not in activity
           Act: Attempt to remove participant that doesn't exist
           Assert: Verify 404 error response
        """
        # Arrange
        test_email = "notregistered@mergington.edu"
        activity_name = "Soccer Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{test_email}"
        )

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"].lower()


    def test_remove_from_nonexistent_activity_fails(self):
        """Arrange: Activity does not exist
           Act: Attempt to remove participant from nonexistent activity
           Assert: Verify 404 error response
        """
        # Arrange
        test_email = "student@mergington.edu"
        nonexistent_activity = "Nonexistent Club"

        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/participants/{test_email}"
        )

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"].lower()
