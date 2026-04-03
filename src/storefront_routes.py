from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from src.db import get_product, list_categories, list_products
from src.web import render_template

router = APIRouter()


@router.get("/", response_class=HTMLResponse, name="index")
def index(request: Request):
    return render_template(
        request,
        "index.html",
        featured_products=list_products(featured_only=True)[:4],
        categories=list_categories(),
    )


@router.get("/about", response_class=HTMLResponse, name="about")
def about(request: Request):
    return render_template(request, "about.html")


@router.get("/category/{category_name}", response_class=HTMLResponse, name="category")
def category(request: Request, category_name: str):
    return render_template(
        request,
        "category.html",
        category_name=category_name,
        products=list_products(category=category_name),
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
