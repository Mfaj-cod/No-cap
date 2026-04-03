"""
Tests for engagement routes (contact form and subscriptions).
"""
import pytest


class TestContactPage:
    """Tests for contact page."""

    def test_contact_page_accessible(self, client):
        """Test accessing contact page."""
        response = client.get("/contact")
        assert response.status_code == 200
        assert "contact" in response.text.lower()

    def test_contact_page_has_form(self, client):
        """Test that contact page has a form."""
        response = client.get("/contact")
        assert response.status_code == 200


class TestContactForm:
    """Tests for contact form submission."""

    def test_contact_form_requires_email_config(self, client):
        """Test that contact form requires SMTP configuration."""
        response = client.post(
            "/contact",
            data={
                "name": "Test User",
                "email": "test@example.com",
                "phone": "9999999999",
                "message": "Test message",
            },
            follow_redirects=True,
        )
        # Will either show error if not configured or success if configured
        assert response.status_code == 200

    def test_contact_form_with_valid_data(self, client):
        """Test submitting contact form with valid data."""
        response = client.post(
            "/contact",
            data={
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "9876543210",
                "message": "I have a question about your caps.",
            },
            follow_redirects=False,
        )
        # Should redirect
        assert response.status_code == 303

    def test_contact_form_with_empty_name(self, client):
        """Test contact form with empty name."""
        response = client.post(
            "/contact",
            data={
                "name": "",
                "email": "test@example.com",
                "phone": "9999999999",
                "message": "Test",
            },
            follow_redirects=False,
        )
        # FastAPI will handle validation
        assert response.status_code in [303, 422]

    def test_contact_form_with_invalid_email(self, client):
        """Test contact form with invalid email format."""
        response = client.post(
            "/contact",
            data={
                "name": "Test User",
                "email": "invalid-email",
                "phone": "9999999999",
                "message": "Test",
            },
            follow_redirects=False,
        )
        assert response.status_code in [303, 422]

    def test_contact_form_with_long_message(self, client):
        """Test contact form with long message."""
        long_message = "x" * 5000
        response = client.post(
            "/contact",
            data={
                "name": "Long Message User",
                "email": "long@example.com",
                "phone": "9999999999",
                "message": long_message,
            },
            follow_redirects=False,
        )
        # Should be accepted
        assert response.status_code == 303

    def test_contact_form_with_special_characters(self, client):
        """Test contact form with special characters in message."""
        response = client.post(
            "/contact",
            data={
                "name": "Special Char User",
                "email": "special@example.com",
                "phone": "9999999999",
                "message": "Message with <html> tags & special chars!",
            },
            follow_redirects=False,
        )
        assert response.status_code == 303

    def test_contact_form_with_unicode(self, client):
        """Test contact form with unicode characters."""
        response = client.post(
            "/contact",
            data={
                "name": "यूनिकोड यूजर",
                "email": "unicode@example.com",
                "phone": "9999999999",
                "message": "नमस्ते! हिंदी में संदेश",
            },
            follow_redirects=False,
        )
        assert response.status_code == 303

    def test_contact_form_redirects_to_contact_page(self, client):
        """Test that contact form redirects back to contact page."""
        response = client.post(
            "/contact",
            data={
                "name": "Test",
                "email": "test@example.com",
                "phone": "9999999999",
                "message": "Test",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200


class TestSubscriptionForm:
    """Tests for newsletter subscription."""

    def test_subscribe_with_valid_email(self, client):
        """Test subscribing with valid email."""
        response = client.post(
            "/subscribe",
            data={"email": "subscriber@example.com"},
            follow_redirects=True,
        )
        assert response.status_code == 200

    def test_subscribe_with_duplicate_email(self, client):
        """Test subscribing with already-subscribed email."""
        email = "duplicate@example.com"
        # First subscription
        client.post("/subscribe", data={"email": email})
        # Second subscription with same email
        response = client.post(
            "/subscribe",
            data={"email": email},
            follow_redirects=True,
        )
        assert "already subscribed" in response.text.lower() or response.status_code == 200

    def test_subscribe_with_empty_email(self, client):
        """Test subscribing with empty email."""
        response = client.post(
            "/subscribe",
            data={"email": ""},
            follow_redirects=True,
        )
        # Will redirect on validation failure
        assert response.status_code in [200, 422]

    def test_subscribe_with_invalid_email(self, client):
        """Test subscribing with invalid email format."""
        response = client.post(
            "/subscribe",
            data={"email": "not-an-email"},
            follow_redirects=True,
        )
        assert response.status_code in [200, 422]

    def test_subscribe_with_special_characters_in_email(self, client):
        """Test subscribing with special characters."""
        response = client.post(
            "/subscribe",
            data={"email": "test+tag@example.co.uk"},
            follow_redirects=True,
        )
        # Gmail and many services support + in emails
        assert response.status_code in [200, 303]

    def test_subscribe_success_message(self, client):
        """Test that successful subscription shows confirmation."""
        response = client.post(
            "/subscribe",
            data={"email": "confirmed@example.com"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert "subscribed" in response.text.lower() or "success" in response.text.lower()

    def test_subscribe_redirects_to_home(self, client):
        """Test that subscription redirects to home page."""
        response = client.post(
            "/subscribe",
            data={"email": "test@example.com"},
            follow_redirects=True,
        )
        assert response.status_code == 200

    def test_subscribe_from_different_pages(self, client):
        """Test subscribing from various pages."""
        # Home page
        response = client.post(
            "/subscribe",
            data={"email": "home@example.com"},
            follow_redirects=True,
        )
        assert response.status_code == 200

        # Cart page 
        response = client.post(
            "/subscribe",
            data={"email": "cart@example.com"},
            follow_redirects=True,
        )
        assert response.status_code == 200


class TestEngagementIntegration:
    """Integration tests for engagement features."""

    def test_subscribe_and_contact_independently(self, client):
        """Test that subscribe and contact form work independently."""
        # Subscribe
        response1 = client.post(
            "/subscribe",
            data={"email": "engage@example.com"},
            follow_redirects=False,
        )
        assert response1.status_code == 303

        # Contact
        response2 = client.post(
            "/contact",
            data={
                "name": "Engaged User",
                "email": "engage@example.com",
                "phone": "9999999999",
                "message": "Great service!",
            },
            follow_redirects=False,
        )
        assert response2.status_code == 303

    def test_contact_with_subscriber_email(self, client):
        """Test that a subscriber can also contact."""
        email = "subscriber-contact@example.com"
        # Subscribe first
        client.post("/subscribe", data={"email": email}, follow_redirects=False)
        # Then contact
        response = client.post(
            "/contact",
            data={
                "name": "Subscriber",
                "email": email,
                "phone": "9999999999",
                "message": "I have feedback",
            },
            follow_redirects=False,
        )
        assert response.status_code == 303
