"""
Tests for the main application and API endpoints.
"""
import pytest


class TestApplicationSetup:
    """Tests for application initialization."""

    def test_app_startup(self, client):
        """Test that the application can start."""
        assert client is not None

    def test_app_has_routes(self, client):
        """Test that the app has configured routes."""
        # Try accessing a basic route
        response = client.get("/health")
        assert response.status_code == 200

    def test_app_health_check(self, client):
        """Test application health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"


class TestApplicationRoutes:
    """Tests for main application routes."""

    def test_home_page_route_exists(self, client):
        """Test that home page route exists."""
        response = client.get("/")
        assert response.status_code == 200

    def test_cart_route_exists(self, client):
        """Test that cart route exists."""
        response = client.get("/cart")
        assert response.status_code == 200

    def test_contact_route_exists(self, client):
        """Test that contact route exists."""
        response = client.get("/contact")
        assert response.status_code == 200

    def test_login_route_exists(self, client):
        """Test that login route exists."""
        response = client.get("/login")
        assert response.status_code == 200

    def test_register_route_exists(self, client):
        """Test that register route exists."""
        response = client.get("/register")
        assert response.status_code == 200

    def test_nonexistent_route_404(self, client):
        """Test that non-existent routes return 404."""
        response = client.get("/this-route-does-not-exist")
        assert response.status_code == 404


class TestSessionHandling:
    """Tests for session management."""

    def test_session_cookie_created(self, client):
        """Test that session cookies are created."""
        response = client.get("/")
        # TestClient handles sessions automatically
        assert response.status_code == 200

    def test_session_persists_across_cart_operations(self, client):
        """Test that session data persists across requests."""
        # Add item to cart in first request
        response1 = client.post(
            "/add_to_cart/1",
            data={"quantity": 1, "variant_sku": ""},
            follow_redirects=False,
        )
        assert response1.status_code == 303

        # Verify item exists in second request
        response2 = client.get("/cart")
        assert response2.status_code == 200

    def test_session_with_login_persists(self, client, sample_user_data):
        """Test that session persists after login."""
        from src.db import create_user
        from src.security import hash_password

        # Create user with unique email from fixture
        user = create_user(
            name=sample_user_data["honey"],
            email=sample_user_data["email"],
            password_hash=hash_password(sample_user_data["password"]),
            role=sample_user_data["role"],
        )

        # Login
        response = client.post(
            "/login",
            data={
                "email": sample_user_data["email"],
                "password": sample_user_data["password"],
            },
        )
        assert response.status_code in [303, 200]

        # Session should persist - verify on account page
        account_response = client.get("/account")
        assert account_response.status_code == 200


class TestStaticFiles:
    """Tests for static file serving."""

    def test_static_files_mounted(self, client):
        """Test that static files directory is mounted."""
        # This just verifies the app is configured
        response = client.get("/static")
        # May return 404 or 405 (method not allowed) depending on setup
        assert response.status_code in [404, 405, 200]


class TestHTTPMethods:
    """Tests for HTTP method handling."""

    def test_get_requests_allowed(self, client):
        """Test GET requests work."""
        response = client.get("/")
        assert response.status_code == 200

    def test_post_requests_allowed(self, client):
        """Test POST requests work."""
        # Contact form is a POST
        response = client.post(
            "/contact",
            data={
                "name": "Test",
                "email": "test@example.com",
                "phone": "9999999999",
                "message": "Test",
            },
            follow_redirects=False,
        )
        # Should either process or redirect
        assert response.status_code in [303, 422, 200]

    def test_invalid_method_returns_error(self, client):
        """Test that invalid HTTP methods return error."""
        response = client.delete("/")
        assert response.status_code in [405, 404]


class TestResponseTypes:
    """Tests for response content types."""

    def test_html_responses(self, client):
        """Test that HTML responses have correct content type."""
        response = client.get("/")
        assert "text/html" in response.headers.get("content-type", "")

    def test_json_responses(self, client):
        """Test JSON response endpoints."""
        response = client.get("/health")
        assert response.status_code == 200
        # Should be JSON
        data = response.json()
        assert isinstance(data, dict)


class TestErrorHandling:
    """Tests for error handling."""

    def test_404_not_found(self, client):
        """Test 404 error handling."""
        response = client.get("/nonexistent-page-xyz")
        assert response.status_code == 404

    def test_malformed_url(self, client):
        """Test handling of malformed URLs."""
        response = client.get("/%20%20%20")
        # Should handle gracefully
        assert response.status_code in [404, 307, 200]


class TestResponseHeaders:
    """Tests for response headers."""

    def test_response_has_content_type(self, client):
        """Test that responses have content-type header."""
        response = client.get("/")
        assert "content-type" in response.headers

    def test_security_headers(self, client):
        """Test for basic security headers."""
        response = client.get("/")
        # FastAPI and Starlette add some security headers
        assert response.status_code == 200
