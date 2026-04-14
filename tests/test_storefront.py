"""
Integration tests for the storefront (public-facing) routes:
  GET  /               (index + search + filters)
  GET  /product/{id}
  GET  /category/{name}
  GET  /about

Also tests the pure-Python _apply_filters and _product_relevance helpers.
"""

import pytest
from src.storefront_routes import _apply_filters, _product_relevance


# Pure-function unit tests

@pytest.mark.unit
class TestApplyFilters:
    """Thin product dicts are enough – no DB required."""

    def _make_products(self):
        return [
            {
                "name": "Velocity Sports Cap",
                "category": "Sports",
                "normal_price": 49.0,
                "featured": True,
                "review_count": 5,
                "total_stock": 100,
                "description": "Lightweight performance cap for training",
                "details": ["Breathable mesh"],
                "attributes": {"Material": "Polyester"},
                "variants": [{"color": "Black", "size": "One Size"}],
            },
            {
                "name": "Weekend Casual Cap",
                "category": "Casual",
                "normal_price": 649.0,
                "featured": True,
                "review_count": 2,
                "total_stock": 95,
                "description": "Classic everyday casual cap",
                "details": ["Soft cotton"],
                "attributes": {"Material": "Cotton"},
                "variants": [{"color": "Tan", "size": "One Size"}],
            },
            {
                "name": "Street Snapback Pro",
                "category": "Snapback",
                "normal_price": 899.0,
                "featured": False,
                "review_count": 0,
                "total_stock": 46,
                "description": "Structured snapback for bold branding",
                "details": ["Flat brim"],
                "attributes": {"Material": "Acrylic"},
                "variants": [{"color": "White", "size": "One Size"}],
            },
        ]

    def test_no_filters_returns_all_products(self):
        products = self._make_products()
        result = _apply_filters(products)
        assert len(result) == 3

    def test_category_filter(self):
        products = self._make_products()
        result = _apply_filters(products, selected_category="Sports")
        assert len(result) == 1
        assert result[0]["category"] == "Sports"

    def test_max_price_filter(self):
        products = self._make_products()
        result = _apply_filters(products, max_price="100")
        assert all(p["normal_price"] <= 100 for p in result)

    def test_max_price_invalid_string_returns_no_price_filter(self):
        products = self._make_products()
        # Invalid max_price → no price filtering
        result = _apply_filters(products, max_price="notanumber")
        assert len(result) == 3

    def test_featured_only_filter(self):
        products = self._make_products()
        result = _apply_filters(products, featured_only=True)
        assert all(p["featured"] for p in result)

    def test_query_filters_by_name(self):
        products = self._make_products()
        result = _apply_filters(products, query="snapback")
        assert len(result) == 1
        assert "Snapback" in result[0]["name"]

    def test_query_no_match_returns_empty(self):
        products = self._make_products()
        result = _apply_filters(products, query="xxxxxxxxxxx")
        assert result == []

    def test_combined_category_and_max_price(self):
        products = self._make_products()
        # Only Sports @ 49.0 passes both
        result = _apply_filters(
            products, selected_category="Sports", max_price="200"
        )
        assert len(result) == 1

    def test_results_sorted_by_featured_then_reviews_when_no_query(self):
        products = self._make_products()
        result = _apply_filters(products)
        # Featured items must come before non-featured
        featured_indices = [i for i, p in enumerate(result) if p["featured"]]
        non_featured_indices = [i for i, p in enumerate(result) if not p["featured"]]
        if featured_indices and non_featured_indices:
            assert max(featured_indices) < min(non_featured_indices)


@pytest.mark.unit
class TestProductRelevance:
    def _product(self):
        return {
            "name": "Velocity Sports Cap",
            "category": "Sports",
            "description": "Lightweight performance cap for training",
            "details": ["Breathable mesh panels"],
            "attributes": {"Material": "Polyester"},
            "variants": [{"color": "Black", "size": "One Size"}],
        }

    def test_name_match_scores_higher_than_description_only(self):
        product = self._product()
        score_name = _product_relevance(product, "velocity")     # name match: 6
        score_desc = _product_relevance(product, "lightweight")  # description match: 3
        assert score_name > score_desc

    def test_category_match_scores_positively(self):
        product = self._product()
        # "sports" matches category (4) AND name (6) = 10
        score = _product_relevance(product, "sports")
        assert score > 0

    def test_empty_query_returns_zero(self):
        assert _product_relevance(self._product(), "") == 0

    def test_irrelevant_query_returns_zero(self):
        assert _product_relevance(self._product(), "xyznotfound") == 0


# HTTP integration tests

@pytest.mark.integration
class TestStorefrontRoutes:
    def test_index_page_loads(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_index_page_contains_products(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        # At least one product name should appear
        assert b"Cap" in resp.content

    def test_index_search_query(self, client):
        resp = client.get("/?q=sports")
        assert resp.status_code == 200

    def test_index_category_filter(self, client):
        resp = client.get("/?category=Sports")
        assert resp.status_code == 200

    def test_index_max_price_filter(self, client):
        resp = client.get("/?max_price=100")
        assert resp.status_code == 200

    def test_index_featured_filter(self, client):
        resp = client.get("/?featured=1")
        assert resp.status_code == 200

    def test_product_detail_page_loads(self, client):
        resp = client.get("/product/1")
        assert resp.status_code == 200
        assert b"Velocity Sports Cap" in resp.content

    def test_product_detail_unknown_id_returns_404(self, client):
        resp = client.get("/product/999999")
        assert resp.status_code == 404

    def test_category_page_loads(self, client):
        resp = client.get("/category/Sports")
        assert resp.status_code == 200

    def test_about_page_loads(self, client):
        resp = client.get("/about")
        assert resp.status_code == 200
