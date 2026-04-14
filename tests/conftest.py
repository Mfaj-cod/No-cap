"""
Shared fixtures for the NoCaps test suite.

All tests share a throwaway SQLite database located in the tests/ directory,
so the production `store.db` is never touched.  The `client` fixture gives
a Starlette TestClient fully wired with sessions and static files.
"""

import os
from pathlib import Path

import pytest
from starlette.testclient import TestClient


# Database isolation

# Path to the ephemeral test DB – lives inside tests/ so no system-tmp perms needed
_TEST_DB = Path(__file__).parent / ".test_store.db"


@pytest.fixture(scope="session", autouse=True)
def _isolated_database():
    """
    Redirect ALL database operations to a local throwaway DB for the session.
    Runs before any other fixture that might import src.db.
    """
    # Remove stale file from a previous interrupted run
    if _TEST_DB.exists():
        try:
            _TEST_DB.unlink()
        except OSError:
            pass

    # Patch the frozen dataclass field at the C level – works for frozen=True
    from src import config
    object.__setattr__(config.settings, "database_path", _TEST_DB)

    # Patch db.py's cached `settings` reference too (it was imported at module load)
    import src.db as db_mod
    # Monkey-patch get_connection so it always uses _TEST_DB
    import sqlite3

    def _test_get_connection():
        conn = sqlite3.connect(str(_TEST_DB))
        conn.row_factory = sqlite3.Row
        return conn

    original_get_connection = db_mod.get_connection
    db_mod.get_connection = _test_get_connection

    # Initialise the schema + seed products/categories into the test DB
    db_mod.init_database()

    yield

    # Restore and clean up
    db_mod.get_connection = original_get_connection
    object.__setattr__(config.settings, "database_path", config.settings.database_path)
    try:
        if _TEST_DB.exists():
            _TEST_DB.unlink()
    except OSError:
        pass


# Application + HTTP client

@pytest.fixture(scope="session")
def app(_isolated_database):
    """Return the FastAPI application, wired to the test database."""
    from app import app as _app
    return _app


@pytest.fixture(scope="session")
def client(app):
    """Session-scoped TestClient – one server start for the whole test run."""
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


# Helper factory: register + login a specific user

@pytest.fixture()
def register_and_login(client):
    """
    Factory fixture.  Call it with (name, email, password, role) and get
    back the login redirect Response (the session cookie is stored in `client`).
    """
    def _factory(name="Test User", email="test@example.com",
                 password="password123", role="customer"):
        client.post(
            "/register",
            data={
                "name": name,
                "email": email,
                "password": password,
                "confirm_password": password,
                "role": role,
            },
            follow_redirects=False,
        )
        return client.post(
            "/login",
            data={"email": email, "password": password},
            follow_redirects=False,
        )

    return _factory
