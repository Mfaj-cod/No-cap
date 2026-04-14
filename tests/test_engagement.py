"""
Integration tests for engagement routes:
  GET  /contact
  POST /contact
  POST /subscribe

Email sending is patched so no real SMTP connection is needed.
"""

import pytest
from unittest.mock import patch
from starlette.testclient import TestClient


def _fresh(app):
    return TestClient(app, raise_server_exceptions=True)


@pytest.mark.integration
class TestContactPage:
    def test_contact_page_loads(self, client):
        resp = client.get("/contact")
        assert resp.status_code == 200

    def test_contact_page_contains_form(self, client):
        resp = client.get("/contact")
        assert b"form" in resp.content.lower()

    @patch("src.engagement_routes.send_contact_message_email")
    def test_contact_post_with_smtp_configured_redirects(self, mock_send, client):
        """
        When SMTP is configured the endpoint calls send_contact_message_email
        (non-blocking) and redirects back to /contact.
        """
        with patch("src.engagement_routes.settings") as mock_settings:
            mock_settings.smtp_user = "test@smtp.com"
            mock_settings.smtp_pass = "password"
            mock_settings.owner_email = "owner@example.com"

            with _fresh(client.app) as c:
                resp = c.post(
                    "/contact",
                    data={
                        "name": "Test User",
                        "email": "user@example.com",
                        "phone": "9876543210",
                        "message": "Hello, I have a question.",
                    },
                    follow_redirects=False,
                )
        assert resp.status_code == 303
        assert "/contact" in resp.headers["location"]

    def test_contact_post_without_smtp_redirects_with_error(self, client):
        """
        When SMTP is not configured the endpoint should not crash –
        it redirects back with a flash message.
        """
        with patch("src.engagement_routes.settings") as mock_settings:
            mock_settings.smtp_user = None
            mock_settings.smtp_pass = None
            mock_settings.owner_email = None

            with _fresh(client.app) as c:
                resp = c.post(
                    "/contact",
                    data={
                        "name": "No SMTP",
                        "email": "user@example.com",
                        "phone": "1234567890",
                        "message": "Testing without SMTP",
                    },
                    follow_redirects=False,
                )
        assert resp.status_code == 303
        assert "/contact" in resp.headers["location"]


@pytest.mark.integration
class TestSubscribe:
    def test_first_subscription_redirects_to_index(self, client):
        with _fresh(client.app) as c:
            resp = c.post(
                "/subscribe",
                data={"email": "subscriber_new@example.com"},
                follow_redirects=False,
            )
        assert resp.status_code == 303
        assert resp.headers["location"].endswith("/")

    def test_duplicate_subscription_redirects_to_index(self, client):
        """Duplicate should not raise – just show 'already subscribed'."""
        email = "subscriber_repeat@example.com"
        with _fresh(client.app) as c:
            c.post("/subscribe", data={"email": email}, follow_redirects=False)
            resp = c.post("/subscribe", data={"email": email}, follow_redirects=False)
        assert resp.status_code == 303
        assert resp.headers["location"].endswith("/")
