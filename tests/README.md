# Nocap Store - Test Suite

This directory contains the comprehensive test suite for the Nocap cap store application.

## Overviewpytest --cov=src --cov-report=html

The test suite covers:
- **Unit Tests**: Individual functions and modules (security, services, configuration)
- **Integration Tests**: API endpoints and database operations
- **Route Tests**: Authentication, cart, orders, storefront, and engagement routes
- **Database Tests**: CRUD operations and schema validation

## Directory Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest configuration and shared fixtures
├── test_config.py           # Configuration and settings tests
├── test_security.py         # Password hashing and verification tests
├── test_services.py         # Cart and checkout services tests
├── test_db.py               # Database operations tests
├── test_auth_routes.py      # Authentication routes tests
├── test_cart_routes.py      # Shopping cart routes tests
├── test_orders_routes.py    # Order processing routes tests
├── test_storefront_routes.py # Product listing and search tests
├── test_engagement_routes.py # Contact form and subscription tests
└── test_app.py              # Main app and health check tests
```

## Test Files Description

### conftest.py
Pytest configuration and shared fixtures:
- `client` - TestClient with session support
- `db_connection` - Direct database connection for testing
- `reset_database` - Automatic database reset before each test
- `sample_user_data` - Sample user account data
- `sample_product_data` - Sample product data
- `logged_in_client` - Pre-authenticated test client

### test_config.py
Tests for configuration settings:
- Settings dataclass properties
- Environment variable loading
- Default values
- Type validation

### test_security.py
Tests for password security:
- Password hashing
- Password verification
- Salting mechanism
- Edge cases (special characters, unicode)

### test_services.py
Tests for business logic:
- Flash messages (add, pop, retrieve)
- Cart operations (add, update, remove, clear)
- Checkout data persistence
- User session management
- Cart item counting

### test_db.py
Tests for database layer:
- User CRUD operations
- Product retrieval
- Category management
- Subscription management
- Database schema validation
- Data seeding

### test_auth_routes.py
Tests for authentication endpoints:
- User registration (customer and shop owner)
- Login functionality
- Logout functionality
- Password validation
- Duplicate email handling
- Account page access

### test_cart_routes.py
Tests for shopping cart endpoints:
- View cart
- Add to cart
- Update cart item quantity
- Remove from cart
- Cart clearing
- Stock validation
- Variant selection

### test_orders_routes.py
Tests for order processing (to be implemented with full order routes):
- Order creation
- Payment processing
- Order status updates
- Order history

### test_storefront_routes.py
Tests for product browsing:
- Home page display
- Product listing
- Search functionality
- Category filtering
- Price filtering
- Featured products
- Product detail pages

### test_engagement_routes.py
Tests for customer engagement:
- Contact form submission
- Input validation
- Email sending
- Newsletter subscription
- Duplicate subscription handling

### test_app.py
Tests for main application:
- Application startup
- Route registration
- Health check endpoint
- Session handling
- Static file serving
- HTTP methods
- Error handling

## Running Tests

### Install Test Dependencies

Add these to your `requirements.txt`:
```
pytest
pytest-asyncio
httpx
```

Or install them:
```bash
pip install pytest pytest-asyncio httpx
```

### Run All Tests

```bash
pytest
```

### Run Tests with Verbose Output

```bash
pytest -v
```

### Run Specific Test File

```bash
pytest tests/test_auth_routes.py
```

### Run Specific Test Class

```bash
pytest tests/test_auth_routes.py::TestLoginRoute
```

### Run Specific Test

```bash
pytest tests/test_auth_routes.py::TestLoginRoute::test_login_success
```

### Run Tests by Marker

```bash
pytest -m unit
pytest -m integration
pytest -m database
```

### Run with Coverage

```bash
pip install pytest-cov
pytest --cov=src --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`.

### Run Tests in Parallel

```bash
pip install pytest-xdist
pytest -n auto
```

## Test Fixtures

### Database Fixtures
- `reset_database` - Creates a fresh test database for each test
- `db_connection` - Direct SQLite connection for manual queries

### Client Fixtures
- `client` - FastAPI TestClient with session support
- `logged_in_client` - Pre-authenticated client for tests requiring login

### Data Fixtures
- `sample_user_data` - Dict with test user credentials
- `sample_shop_owner_data` - Dict with test shop owner credentials
- `sample_product_data` - Dict with test product info

## Writing New Tests

### Example Test Structure

```python
class TestFeature:
    """Tests for specific feature."""
    
    def test_specific_scenario(self, client):
        """Test description."""
        response = client.get("/route")
        assert response.status_code == 200
    
    def test_error_case(self, client):
        """Test error handling."""
        response = client.post("/submit", data={})
        assert response.status_code == 422
```

### Using Fixtures

```python
def test_with_user(self, client, sample_user_data):
    """Test with sample user data."""
    response = client.post("/login", data=sample_user_data)
    assert response.status_code == 303
```

### Database Testing

```python
def test_database_query(self, db_connection):
    """Test database operation."""
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    assert len(users) >= 0
```

## Best Practices

1. **Isolation**: Each test should be independent and not rely on others
2. **Cleanup**: Database is automatically reset before each test
3. **Descriptive Names**: Test names should describe what they test
4. **Assertions**: Use clear assertions with meaningful failure messages
5. **Fixtures**: Use fixtures for common setup (don't repeat code)
6. **Coverage**: Aim for high code coverage especially for critical paths

## Continuous Integration

To run tests in CI/CD:

```bash
pytest --cov=src --cov-report=xml
```

Then upload `coverage.xml` to your CI service.

## Debugging Tests

### Run with Print Output

```bash
pytest -s
```

This shows print statements and log output.

### Run with Python Debugger

```bash
pytest --pdb
```

Drops into debugger on failures.

### Run Specific Test with Verbose Output

```bash
pytest tests/test_auth_routes.py::TestLoginRoute::test_login_success -vv -s
```

## Common Issues

### Database Locked Error
- The test database is created fresh for each test
- If you get "database locked", it usually means cleanup failed
- Check that all connections are properly closed

### Session Not Persisting
- The test client uses in-memory sessions
- Session data is available via `client.session_transaction()`

### Static Files Not Found
- Tests use the app with static files mounted
- Static files are accessed relative to the app root

## Future Test Coverage

Areas that need additional test coverage:
- [ ] Complete order routes tests
- [ ] Payment integration tests
- [ ] Email functionality tests
- [ ] AI support response tests
- [ ] Wholesale pricing logic tests
- [ ] Complex filtering and search tests
- [ ] Performance and load tests

## Contributing Tests

When adding new features:
1. Write tests first (TDD recommended)
2. Ensure tests pass
3. Maintain or improve code coverage
4. Update this README if adding new test files

## References

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/advanced/testing-dependencies/)
- [SQLite Testing Best Practices](https://www.sqlite.org/testing.html)
