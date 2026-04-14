"""
Health-check endpoint – the very first thing CI should verify.
"""

import pytest


@pytest.mark.integration
def test_healthcheck_returns_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data == {"status": "ok"}
