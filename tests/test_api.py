"""
Unit tests for the Mergington High School API.

All tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and fixtures
- Act: Execute the API call
- Assert: Verify the response status, data, and side effects
"""


class TestRootEndpoint:
    """Tests for GET / endpoint (redirect to static files)."""

    def test_root_redirect_to_static_index(self, client):
        """
        Arrange: No setup needed - test redirect
        Act: Make GET request to /
        Assert: Should redirect (status 307) to /static/index.html
        """
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivitiesEndpoint:
    """Tests for GET /activities endpoint."""

    def test_get_all_activities_success(self, client):
        """
        Arrange: Client connected to app with default activities
        Act: Make GET request to /activities
        Assert: Should return 200 with all activities and correct structure
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Verify all 9 activities are present
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert "Soccer Team" in data
        assert "Basketball Club" in data
        assert "Art Club" in data
        assert "Drama Club" in data
        assert "Debate Team" in data
        assert "Science Olympiad" in data

    def test_get_activities_has_correct_structure(self, client):
        """
        Arrange: Client connected to app
        Act: Make GET request to /activities
        Assert: Each activity should have description, schedule, max_participants, participants
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        
        for activity_name, activity in data.items():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)

    def test_get_activities_initial_participants(self, client):
        """
        Arrange: Client with default activities
        Act: Make GET request to /activities
        Assert: Chess Club should have michael and daniel as participants
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        chess_participants = data["Chess Club"]["participants"]
        
        assert "michael@mergington.edu" in chess_participants
        assert "daniel@mergington.edu" in chess_participants
        assert len(chess_participants) == 2


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client):
        """
        Arrange: Valid activity name and new email address
        Act: POST request to /activities/Chess Club/signup with new email
        Assert: Should return 200 and email should be added to participants
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert email in data["message"]
        
        # Verify email was added to participants
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity_name]["participants"]

    def test_signup_duplicate_email(self, client):
        """
        Arrange: Valid activity and email already in participants
        Act: POST request to signup with duplicate email
        Assert: Should add email again (no validation in current implementation)
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already a participant
        initial_count = len(client.get("/activities").json()[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        
        # Verify email was added (duplicate signup is allowed in current implementation)
        activities_response = client.get("/activities")
        final_count = len(activities_response.json()[activity_name]["participants"])
        assert final_count == initial_count + 1

    def test_signup_invalid_activity_not_found(self, client):
        """
        Arrange: Non-existent activity name
        Act: POST request to /activities/Invalid Activity/signup
        Assert: Should return 404 error
        """
        # Arrange
        activity_name = "Non-existent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_multiple_students(self, client):
        """
        Arrange: Multiple different students signing up for same activity
        Act: POST requests for each student
        Assert: All should succeed and all emails should be in participants
        """
        # Arrange
        activity_name = "Programming Class"
        emails = ["alice@mergington.edu", "bob@mergington.edu", "charlie@mergington.edu"]

        # Act
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200

        # Assert
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        for email in emails:
            assert email in participants


class TestUnregisterEndpoint:
    """Tests for POST /activities/{activity_name}/unregister endpoint."""

    def test_unregister_success(self, client):
        """
        Arrange: Valid activity and email that is in participants
        Act: POST request to /activities/Chess Club/unregister with existing email
        Assert: Should return 200 and email should be removed from participants
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Verify email is in participants before unregistering
        pre_response = client.get("/activities")
        assert email in pre_response.json()[activity_name]["participants"]

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert email in data["message"]
        
        # Verify email was removed from participants
        post_response = client.get("/activities")
        assert email not in post_response.json()[activity_name]["participants"]

    def test_unregister_email_not_in_activity(self, client):
        """
        Arrange: Valid activity but email not in participants
        Act: POST request to unregister with email that was never signed up
        Assert: Should return 404 error (Participant not found)
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notasignup@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]

    def test_unregister_invalid_activity(self, client):
        """
        Arrange: Non-existent activity name
        Act: POST request to /activities/Invalid Activity/unregister
        Assert: Should return 404 error (Activity not found)
        """
        # Arrange
        activity_name = "Non-existent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_then_signup_again(self, client):
        """
        Arrange: Valid activity and email currently in participants
        Act: Unregister the email, then sign up again
        Assert: Both operations should succeed and email count should return to original
        """
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"
        initial_count = len(client.get("/activities").json()[activity_name]["participants"])

        # Act - Unregister
        unregister_response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        mid_count = len(client.get("/activities").json()[activity_name]["participants"])
        assert mid_count == initial_count - 1

        # Act - Sign up again
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        final_count = len(client.get("/activities").json()[activity_name]["participants"])

        # Assert
        assert final_count == initial_count


class TestIntegrationScenarios:
    """Integration tests combining multiple endpoint scenarios."""

    def test_signup_and_verify_participant_count(self, client):
        """
        Arrange: Activity with known participant count
        Act: Sign up new students and check count increases
        Assert: Participant count should increase correctly
        """
        # Arrange
        activity_name = "Soccer Team"
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])

        # Act
        emails = ["new1@mergington.edu", "new2@mergington.edu"]
        for email in emails:
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )

        # Assert
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity_name]["participants"])
        assert final_count == initial_count + len(emails)

    def test_full_lifecycle_signup_unregister_signup(self, client):
        """
        Arrange: New student and activity
        Act: Sign up, unregister, and sign up again
        Assert: All operations should succeed with correct state
        """
        # Arrange
        activity_name = "Basketball Club"
        email = "newbasketball@mergington.edu"

        # Act & Assert - Step 1: Sign up
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        assert email in client.get("/activities").json()[activity_name]["participants"]

        # Act & Assert - Step 2: Unregister
        response2 = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response2.status_code == 200
        assert email not in client.get("/activities").json()[activity_name]["participants"]

        # Act & Assert - Step 3: Sign up again
        response3 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response3.status_code == 200
        assert email in client.get("/activities").json()[activity_name]["participants"]

    def test_multiple_activities_independent(self, client):
        """
        Arrange: Two different activities
        Act: Sign up for both, unregister from one
        Assert: Changes should only affect the targeted activity
        """
        # Arrange
        activity1 = "Art Club"
        activity2 = "Drama Club"
        email = "multiactivity@mergington.edu"

        # Act - Sign up for both
        client.post(f"/activities/{activity1}/signup", params={"email": email})
        client.post(f"/activities/{activity2}/signup", params={"email": email})

        # Assert - Both should have the email
        activities_data = client.get("/activities").json()
        assert email in activities_data[activity1]["participants"]
        assert email in activities_data[activity2]["participants"]

        # Act - Unregister from activity1 only
        client.post(f"/activities/{activity1}/unregister", params={"email": email})

        # Assert - Only activity1 should be affected
        activities_data = client.get("/activities").json()
        assert email not in activities_data[activity1]["participants"]
        assert email in activities_data[activity2]["participants"]
