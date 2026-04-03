"""
Pytest configuration and shared fixtures for the Nocap test suite.
"""
import os
import sqlite3
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from starlette.middleware.sessions import SessionMiddleware
from starlette.testclient import TestClient as StarletteTestClient

from app import app
from src.config import settings, Settings
from src.db import get_connection, init_database


@pytest.fixture(scope="session")
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    yield db_path
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture(autouse=True)
def reset_database(monkeypatch, temp_db):
    """Reset database before each test."""
    # Use a fresh test database for each test
    test_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    test_db_path = test_db.name
    test_db.close()

    # Create a new settings instance with test database path
    import src.config
    test_settings = Settings(
        store_name=src.config.settings.store_name,
        database_path=Path(test_db_path),
        session_secret=src.config.settings.session_secret,
        razorpay_key_id=src.config.settings.razorpay_key_id,
        razorpay_key_secret=src.config.settings.razorpay_key_secret,
        smtp_server=src.config.settings.smtp_server,
        smtp_port=src.config.settings.smtp_port,
        smtp_user=src.config.settings.smtp_user,
        smtp_pass=src.config.settings.smtp_pass,
        owner_email=src.config.settings.owner_email,
        groq_api_key=src.config.settings.groq_api_key,
        groq_model=src.config.settings.groq_model,
    )
    
    monkeypatch.setattr("src.config.settings", test_settings)
    
    # Initialize the test database with schema
    init_database()

    yield test_db_path

    # Cleanup
    if os.path.exists(test_db_path):
        os.unlink(test_db_path)


@pytest.fixture
def client(reset_database):
    """Create a test client with session support."""
    return TestClient(app)


@pytest.fixture
def db_connection(reset_database):
    """Get a database connection for direct testing."""
    conn = get_connection()
    yield conn
    conn.close()


@pytest.fixture
def sample_user_data():
    """Fixture for sample user data."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return {
        "name": "John Doe",
        "email": f"john_{unique_id}@example.com",
        "password": "password123",
        "role": "customer",
    }


@pytest.fixture
def sample_shop_owner_data():
    """Fixture for sample shop owner data."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return {
        "name": "Shop Owner",
        "email": f"owner_{unique_id}@example.com",
        "password": "password123",
        "role": "shop_owner",
    }


@pytest.fixture
def logged_in_client(client, sample_user_data):
    """Create a client with a logged-in user."""
    from src.db import create_user
    from src.security import hash_password

    create_user(
        name=sample_user_data["name"],
        email=sample_user_data["email"],
        password_hash=hash_password(sample_user_data["password"]),
        role=sample_user_data["role"],
    )

    response = client.post(
        "/login",
        data={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"],
        },
        follow_redirects=False,
    )

    # Extract session cookie
    if "set-cookie" in response.headers:
        cookies = response.headers.get("set-cookie", "")
        if "session=" in cookies:
            # Session middleware handles cookies automatically with TestClient
            pass

    return client, sample_user_data


@pytest.fixture
def sample_product_data():
    """Fixture for sample product in database."""
    from src.db import get_connection

    conn = get_connection()
    cursor = conn.cursor()

    product_data = {
        "id": 1,
        "name": "Test Cap",
        "description": "A test cap",
        "normal_price": 500.0,
        "image_url": "/static/img/test.jpg",
        "category": "Sports",
        "details": '["Comfortable", "Durable"]',
        "attributes": '{"material": "cotton", "size": "One Size"}',
        "media_gallery": '[]',
        "variants": '[{"sku": "TEST-001", "color": "Black", "size": "OS", "stock_quantity": 100}]',
        "reviews": '[]',
        "featured": 0,
    }

    cursor.execute(
        """
        INSERT INTO products
        (id, name, description, normal_price, image_url, category, details,
         attributes, media_gallery, variants, reviews, featured)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            product_data["id"],
            product_data["name"],
            product_data["description"],
            product_data["normal_price"],
            product_data["image_url"],
            product_data["category"],
            product_data["details"],
            product_data["attributes"],
            product_data["media_gallery"],
            product_data["variants"],
            product_data["reviews"],
            product_data["featured"],
        ),
    )
    conn.commit()
    conn.close()

    return product_data
