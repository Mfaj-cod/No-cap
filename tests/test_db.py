"""
Tests for database module.
"""
import pytest
import sqlite3

from src.db import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    list_products,
    get_product,
    list_categories,
    create_subscription,
)
from src.security import hash_password


class TestUserOperations:
    """Tests for user-related database operations."""

    def test_create_user(self, db_connection):
        """Test creating a new user."""
        from src.db import create_user, get_user_by_email
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        email = f"test_create_{unique_id}@example.com"
        create_user(
            name="Test User",
            email=email,
            password_hash=hash_password("password123"),
            role="customer",
        )
        
        user = get_user_by_email(email)
        assert user is not None
        assert user["name"] == "Test User"
        assert user["email"] == email
        assert user["role"] == "customer"

    def test_create_duplicate_user_email(self, db_connection):
        """Test that duplicate email raises IntegrityError."""
        from src.db import create_user
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        email = f"duplicate_test_{unique_id}@example.com"
        create_user(
            name="User 1",
            email=email,
            password_hash=hash_password("pass1"),
            role="customer",
        )

        with pytest.raises(sqlite3.IntegrityError):
            create_user(
                name="User 2",
                email=email,
                password_hash=hash_password("pass2"),
                role="customer",
            )

    def test_get_user_by_email(self, db_connection):
        """Test retrieving user by email."""
        from src.db import create_user, get_user_by_email
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        email = f"test_get_email_{unique_id}@example.com"
        create_user(
            name="John Doe",
            email=email,
            password_hash=hash_password("password"),
            role="customer",
        )

        found = get_user_by_email(email)
        assert found is not None
        assert found["name"] == "John Doe"

    def test_get_user_by_email_not_found(self, db_connection):
        """Test retrieving non-existent user by email."""
        from src.db import get_user_by_email

        user = get_user_by_email("nonexistent@example.com")
        assert user is None

    def test_get_user_by_id(self, db_connection):
        """Test retrieving user by ID."""
        from src.db import create_user, get_user_by_id, get_user_by_email
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        email = f"test_get_id_{unique_id}@example.com"
        create_user(
            name="Jane Doe",
            email=email,
            password_hash=hash_password("password"),
            role="shop_owner",
        )

        created = get_user_by_email(email)
        found = get_user_by_id(created["id"])
        assert found is not None
        assert found["email"] == email

    def test_get_user_by_id_not_found(self, db_connection):
        """Test retrieving non-existent user by ID."""
        from src.db import get_user_by_id

        user = get_user_by_id(99999)
        assert user is None


class TestProductOperations:
    """Tests for product-related database operations."""

    def test_list_products_returns_list(self, db_connection):
        """Test that list_products returns a list."""
        products = list_products()
        assert isinstance(products, list)
        # Should have seed data from initialization
        assert len(products) > 0

    def test_list_products_with_featured_only(self, db_connection):
        """Test filtering products by featured status."""
        featured_products = list_products(featured_only=True)
        assert isinstance(featured_products, list)
        # All should have featured=True
        for product in featured_products:
            assert product["featured"] == 1 or product["featured"] is True

    def test_get_product_by_id(self, db_connection):
        """Test retrieving a product by ID."""
        products = list_products()
        if products:
            product = get_product(products[0]["id"])
            assert product is not None
            assert product["id"] == products[0]["id"]

    def test_get_product_not_found(self, db_connection):
        """Test retrieving non-existent product."""
        product = get_product(99999)
        assert product is None

    def test_product_has_required_fields(self, db_connection):
        """Test that products have all required fields."""
        product = get_product(1)
        if product:
            required_fields = [
                "id",
                "name",
                "description",
                "normal_price",
                "category",
                "variants",
                "reviews",
                "featured",
            ]
            for field in required_fields:
                assert field in product


class TestCategoryOperations:
    """Tests for category-related database operations."""

    def test_list_categories(self, db_connection):
        """Test listing all categories."""
        categories = list_categories()
        assert isinstance(categories, list)
        assert len(categories) > 0  # Should have seed data

    def test_categories_have_required_fields(self, db_connection):
        """Test that categories have required fields."""
        categories = list_categories()
        if categories:
            for category in categories:
                assert "name" in category
                assert "image_url" in category


class TestSubscriptionOperations:
    """Tests for subscription management."""

    def test_create_subscription(self, db_connection):
        """Test creating a subscription."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        email = f"subscriber_{unique_id}@example.com"
        result = create_subscription(email)
        assert result is True

    def test_create_duplicate_subscription(self, db_connection):
        """Test that duplicate subscription returns False."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        email = f"duplicate_{unique_id}@example.com"
        create_subscription(email)
        result = create_subscription(email)
        assert result is False

    def test_get_subscription(self, db_connection):
        """Test retrieving a subscription from database."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        email = f"test-sub_{unique_id}@example.com"
        create_subscription(email)
        
        # Query database directly to verify subscription exists
        cursor = db_connection.cursor()
        cursor.execute("SELECT * FROM subscriptions WHERE email = ?", (email,))
        sub = cursor.fetchone()
        assert sub is not None
        assert sub["email"] == email

    def test_get_subscription_not_found(self, db_connection):
        """Test retrieving non-existent subscription."""
        cursor = db_connection.cursor()
        cursor.execute("SELECT * FROM subscriptions WHERE email = ?", ("nonexistent@example.com",))
        sub = cursor.fetchone()
        assert sub is None


class TestDatabaseInitialization:
    """Tests for database initialization and schema."""

    def test_database_has_required_tables(self, db_connection):
        """Test that database has all required tables."""
        cursor = db_connection.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row[0] for row in cursor.fetchall()]

        required_tables = [
            "users",
            "products",
            "categories",
            "orders",
            "order_items",
            "subscriptions",
        ]
        for table in required_tables:
            assert table in tables

    def test_users_table_schema(self, db_connection):
        """Test users table has correct schema."""
        cursor = db_connection.cursor()
        cursor.execute("PRAGMA table_info(users)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}

        expected_columns = {
            "id": "INTEGER",
            "name": "TEXT",
            "email": "TEXT",
            "password_hash": "TEXT",
            "role": "TEXT",
            "created_at": "TIMESTAMP",
        }
        for col_name, col_type in expected_columns.items():
            assert col_name in columns

    def test_products_table_has_data(self, db_connection):
        """Test that products table is seeded with data."""
        products = list_products()
        assert len(products) > 0
