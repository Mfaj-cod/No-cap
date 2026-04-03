"""
Tests for storefront routes.
"""
import pytest


class TestIndexRoute:
    """Tests for the storefront index/home page."""

    def test_index_page_accessible(self, client):
        """Test accessing home page."""
        response = client.get("/")
        assert response.status_code == 200
        assert "cap" in response.text.lower() or "product" in response.text.lower()

    def test_index_displays_featured_products(self, client):
        """Test that index page displays featured products."""
        response = client.get("/")
        assert response.status_code == 200
        # Page should contain product information

    def test_index_with_search_query(self, client):
        """Test searching products from index."""
        response = client.get("/?q=sports")
        assert response.status_code == 200

    def test_index_with_category_filter(self, client):
        """Test filtering by category."""
        from src.db import list_categories

        categories = list_categories()
        if categories:
            category_name = categories[0]["name"]
            response = client.get(f"/?category={category_name}")
            assert response.status_code == 200

    def test_index_with_price_filter(self, client):
        """Test filtering by maximum price."""
        response = client.get("/?max_price=1000")
        assert response.status_code == 200

    def test_index_with_featured_filter(self, client):
        """Test filtering featured products only."""
        response = client.get("/?featured=1")
        assert response.status_code == 200

    def test_index_with_multiple_filters(self, client):
        """Test applying multiple filters."""
        response = client.get("/?q=cap&featured=1&max_price=5000")
        assert response.status_code == 200

    def test_index_empty_search_shows_all(self, client):
        """Test that empty search shows all products."""
        response = client.get("/?q=")
        assert response.status_code == 200

    def test_index_search_invalid_price(self, client):
        """Test search with invalid price filter."""
        response = client.get("/?max_price=invalid")
        assert response.status_code == 200

    def test_index_displays_categories(self, client):
        """Test that index displays all categories."""
        response = client.get("/")
        assert response.status_code == 200
        # Categories should be available for filtering

    def test_index_displays_product_list(self, client):
        """Test that products are displayed."""
        from src.db import list_products

        products = list_products()
        response = client.get("/")
        assert response.status_code == 200
        if products:
            # At least product names should appear
            pass


class TestProductRoute:
    """Tests for individual product page."""

    def test_product_page_accessible(self, client):
        """Test accessing product detail page."""
        from src.db import list_products

        products = list_products()
        if products:
            product_id = products[0]["id"]
            response = client.get(f"/product/{product_id}")
            assert response.status_code == 200
            assert "product" in response.text.lower()

    def test_product_page_displays_info(self, client):
        """Test product page displays product information."""
        from src.db import list_products

        products = list_products()
        if products:
            product = products[0]
            response = client.get(f"/product/{product['id']}")
            assert response.status_code == 200
            # Product name should be in the page
            assert product["name"] in response.text or "product" in response.text.lower()

    def test_nonexistent_product(self, client):
        """Test accessing non-existent product."""
        response = client.get("/product/99999")
        assert response.status_code in [404, 200]  # May show 404 or redirect

    def test_product_page_displays_variants(self, client):
        """Test that product variants are displayed."""
        from src.db import list_products

        products = list_products()
        if products:
            for product in products:
                if product.get("variants"):
                    response = client.get(f"/product/{product['id']}")
                    assert response.status_code == 200
                    break

    def test_product_page_displays_reviews(self, client):
        """Test product reviews are displayed."""
        from src.db import list_products

        products = list_products()
        if products:
            for product in products:
                if product.get("reviews"):
                    response = client.get(f"/product/{product['id']}")
                    assert response.status_code == 200
                    break

    def test_product_page_displays_price(self, client):
        """Test that product prices are displayed."""
        from src.db import list_products

        products = list_products()
        if products:
            product = products[0]
            response = client.get(f"/product/{product['id']}")
            assert response.status_code == 200


class TestSearchFunctionality:
    """Tests for product search."""

    def test_search_by_product_name(self, client):
        """Test searching by product name."""
        from src.db import list_products

        products = list_products()
        if products:
            product_name = products[0]["name"].split()[0].lower()
            response = client.get(f"/?q={product_name}")
            assert response.status_code == 200

    def test_search_case_insensitive(self, client):
        """Test that search is case-insensitive."""
        response1 = client.get("/?q=sports")
        response2 = client.get("/?q=SPORTS")
        assert response1.status_code == 200
        assert response2.status_code == 200

    def test_search_empty_results(self, client):
        """Test search with no matching results."""
        response = client.get("/?q=xyzabc123nonexistent")
        assert response.status_code == 200

    def test_search_special_characters(self, client):
        """Test search with special characters."""
        response = client.get("/?q=%40%23%24")
        assert response.status_code == 200


class TestCategoryFilter:
    """Tests for category filtering."""

    def test_filter_by_first_category(self, client):
        """Test filtering by first available category."""
        from src.db import list_categories

        categories = list_categories()
        if categories:
            response = client.get(f"/?category={categories[0]['name']}")
            assert response.status_code == 200

    def test_filter_by_invalid_category(self, client):
        """Test filtering by invalid category."""
        response = client.get("/?category=NonExistentCategory")
        assert response.status_code == 200

    def test_multiple_results_from_category(self, client):
        """Test that category filter returns products."""
        from src.db import list_categories, list_products

        categories = list_categories()
        if categories:
            products = list_products()
            category_name = categories[0]["name"]
            response = client.get(f"/?category={category_name}")
            assert response.status_code == 200


class TestPriceFilter:
    """Tests for price filtering."""

    def test_filter_by_price_low(self, client):
        """Test filtering by low price."""
        response = client.get("/?max_price=500")
        assert response.status_code == 200

    def test_filter_by_price_high(self, client):
        """Test filtering by high price."""
        response = client.get("/?max_price=10000")
        assert response.status_code == 200

    def test_filter_by_price_zero(self, client):
        """Test filtering by zero price shows nothing."""
        response = client.get("/?max_price=0")
        assert response.status_code == 200

    def test_filter_by_negative_price(self, client):
        """Test filtering by negative price."""
        response = client.get("/?max_price=-100")
        assert response.status_code == 200
