"""
Integration tests for the admin routes:
  GET  /admin/orders               – requires admin role
  GET  /api/admin/orders           – requires admin role (JSON)
  POST /api/admin/orders/{id}/status – requires admin role

Non-admin access should receive HTTP 403.
"""

import pytest
from starlette.testclient import TestClient


_admin_counter = 0


def _fresh(app):
    return TestClient(app, raise_server_exceptions=True)


def _admin_email():
    global _admin_counter
    _admin_counter += 1
    return f"admin_test_{_admin_counter}@example.com"


def _make_admin_client(app):
    """Register a user, then upgrade them to admin directly in the DB."""
    email = _admin_email()
    c = TestClient(app, raise_server_exceptions=True)
    c.__enter__()

    # Register
    c.post(
        "/register",
        data={
            "name": "Admin User",
            "email": email,
            "password": "adminpass123",
            "confirm_password": "adminpass123",
            "role": "customer",
        },
        follow_redirects=True,
    )

    # Promote to admin directly in DB
    from src.db import get_connection, get_user_by_email
    user = get_user_by_email(email)
    conn = get_connection()
    conn.execute("UPDATE users SET role = 'admin' WHERE id = ?", (user["id"],))
    conn.commit()
    conn.close()

    # Re-login so the session picks up the updated role check
    # (The role is checked in get_current_user which reads from DB each time)
    c.post(
        "/login",
        data={"email": email, "password": "adminpass123"},
        follow_redirects=True,
    )
    return c


@pytest.mark.integration
class TestAdminRoutes:
    def test_admin_orders_page_requires_auth(self, client):
        with _fresh(client.app) as c:
            resp = c.get("/admin/orders")
        assert resp.status_code == 403

    def test_admin_orders_page_accessible_to_admin(self, client):
        with _make_admin_client(client.app) as c:
            resp = c.get("/admin/orders")
        assert resp.status_code == 200

    def test_non_admin_customer_gets_403(self, client):
        with _fresh(client.app) as c:
            email = f"nonadmin_{_admin_counter}@example.com"
            c.post(
                "/register",
                data={
                    "name": "Customer",
                    "email": email,
                    "password": "pass1234",
                    "confirm_password": "pass1234",
                    "role": "customer",
                },
                follow_redirects=True,
            )
            resp = c.get("/admin/orders")
        assert resp.status_code == 403

    def test_api_list_orders_requires_admin(self, client):
        with _fresh(client.app) as c:
            resp = c.get("/api/admin/orders")
        assert resp.status_code == 403

    def test_api_list_orders_returns_json_for_admin(self, client):
        with _make_admin_client(client.app) as c:
            resp = c.get("/api/admin/orders")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_api_list_orders_filters_out_cancelled(self, client):
        with _make_admin_client(client.app) as c:
            resp = c.get("/api/admin/orders")
        data = resp.json()
        for order in data:
            assert order["status"] not in ("cancelled", "failed")

    def test_api_update_order_status_requires_admin(self, client):
        with _fresh(client.app) as c:
            resp = c.post(
                "/api/admin/orders/1/status",
                json={"status": "confirmed"},
            )
        assert resp.status_code == 403

    def test_api_update_order_status_missing_status_returns_400(self, client):
        with _make_admin_client(client.app) as c:
            # Place an order first to get a valid order ID
            c.post(
                "/add_to_cart/1",
                data={"quantity": "1", "variant_sku": "VEL-BLK-OS"},
                follow_redirects=True,
            )
            checkout_resp = c.post(
                "/checkout",
                data={
                    "name": "Admin Buyer",
                    "email": "adminbuyer@example.com",
                    "phone": "9876543210",
                    "address": "123 Admin St",
                    "city": "Delhi",
                    "state": "Delhi",
                    "pincode": "110001",
                    "payment_method": "cod",
                },
                follow_redirects=False,
            )
            order_id = checkout_resp.headers["location"].split("order_id=")[1]
            resp = c.post(
                f"/api/admin/orders/{order_id}/status",
                json={},  # missing 'status'
            )
        assert resp.status_code == 400

    def test_api_update_order_status_success(self, client):
        with _make_admin_client(client.app) as c:
            c.post(
                "/add_to_cart/1",
                data={"quantity": "1", "variant_sku": "VEL-RED-OS"},
                follow_redirects=True,
            )
            checkout_resp = c.post(
                "/checkout",
                data={
                    "name": "Admin Buyer2",
                    "email": "adminbuyer2@example.com",
                    "phone": "9000000001",
                    "address": "456 Admin Ave",
                    "city": "Chennai",
                    "state": "Tamil Nadu",
                    "pincode": "600001",
                    "payment_method": "cod",
                },
                follow_redirects=False,
            )
            order_id = checkout_resp.headers["location"].split("order_id=")[1]
            resp = c.post(
                f"/api/admin/orders/{order_id}/status",
                json={"status": "confirmed"},
            )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["order"]["status"] == "confirmed"
