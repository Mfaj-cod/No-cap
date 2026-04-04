from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from src.db import get_product, list_categories, list_products
from src.web import render_template
from fastapi.responses import JSONResponse
from src.web import _collect_gallery_images

router = APIRouter()


def _product_relevance(product: dict, query: str) -> int:
    terms = [term for term in query.lower().split() if term]
    if not terms:
        return 0

    details_text = " ".join(product["details"]).lower()
    attribute_text = " ".join(str(value) for value in product["attributes"].values()).lower()
    variant_text = " ".join(
        f"{variant.get('color', '')} {variant.get('size', '')}".strip()
        for variant in product["variants"]
    ).lower()

    score = 0
    for term in terms:
        if term in product["name"].lower():
            score += 6
        if term in product["category"].lower():
            score += 4
        if term in product["description"].lower():
            score += 3
        if term in details_text:
            score += 2
        if term in attribute_text:
            score += 2
        if term in variant_text:
            score += 2
    return score


def _apply_filters(
    products: list[dict],
    query: str = "",
    selected_category: str = "",
    max_price: str = "",
    featured_only: bool = False,
) -> list[dict]:
    filtered = products

    if selected_category:
        filtered = [product for product in filtered if product["category"] == selected_category]

    if max_price:
        try:
            ceiling = float(max_price)
        except ValueError:
            ceiling = 0
        if ceiling:
            filtered = [product for product in filtered if product["normal_price"] <= ceiling]

    if featured_only:
        filtered = [product for product in filtered if product["featured"]]

    if query:
        scored = []
        for product in filtered:
            score = _product_relevance(product, query)
            if score > 0:
                scored.append((score, product))
        scored.sort(key=lambda item: (item[0], item[1]["featured"], item[1]["review_count"], item[1]["total_stock"]), reverse=True)
        return [product for _, product in scored]

    return sorted(filtered, key=lambda product: (product["featured"], product["review_count"], product["total_stock"]), reverse=True)


@router.get("/", response_class=HTMLResponse, name="index")
def index(request: Request):
    filters = {
        "q": request.query_params.get("q", "").strip(),
        "category": request.query_params.get("category", "").strip(),
        "max_price": request.query_params.get("max_price", "").strip(),
        "featured": request.query_params.get("featured") == "1",
    }
    all_products = list_products()
    browse_results = _apply_filters(
        all_products,
        query=filters["q"],
        selected_category=filters["category"],
        max_price=filters["max_price"],
        featured_only=filters["featured"],
    )

    return render_template(
        request,
        "index.html",
        featured_products=list_products(featured_only=True)[:4],
        browse_results=browse_results,
        categories=list_categories(),
        filters=filters,
        has_filters=bool(filters["q"] or filters["category"] or filters["max_price"] or filters["featured"]),
    )


@router.get("/about", response_class=HTMLResponse, name="about")
def about(request: Request):
    return render_template(request, "about.html")


@router.get("/category/{category_name}", response_class=HTMLResponse, name="category")
def category(request: Request, category_name: str):
    filters = {
        "q": request.query_params.get("q", "").strip(),
        "max_price": request.query_params.get("max_price", "").strip(),
        "featured": request.query_params.get("featured") == "1",
    }
    products = _apply_filters(
        list_products(category=category_name),
        query=filters["q"],
        max_price=filters["max_price"],
        featured_only=filters["featured"],
    )
    return render_template(
        request,
        "category.html",
        category_name=category_name,
        products=products,
        filters=filters,
    )


@router.get("/product/{product_id}", response_class=HTMLResponse, name="product")
def product(request: Request, product_id: int):
    selected_product = get_product(product_id)
    if not selected_product:
        return HTMLResponse("Product not found", status_code=404)

    related_products = [
        product
        for product in list_products(category=selected_product["category"])
        if product["id"] != selected_product["id"]
    ][:4]
    return render_template(
        request,
        "product.html",
        product=selected_product,
        related_products=related_products,
    )


@router.get('/_debug/gallery_images', response_class=JSONResponse, name='debug_gallery')
def debug_gallery(request: Request):
    """Debug endpoint: return the gallery image paths collected by web._collect_gallery_images()."""
    imgs = _collect_gallery_images(100)
    return JSONResponse({'count': len(imgs), 'images': imgs})
