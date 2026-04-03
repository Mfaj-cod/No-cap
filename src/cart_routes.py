from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from src.db import get_product, get_variant_for_product
from src.services import add_flash, build_cart_key, build_cart_summary, get_cart, get_current_user, parse_cart_key, save_cart
from src.web import render_template

router = APIRouter()


@router.get("/cart", response_class=HTMLResponse, name="cart")
def cart_page(request: Request):
    return render_template(
        request,
        "cart.html",
        cart_summary=build_cart_summary(request, get_current_user(request)),
    )


@router.post("/add_to_cart/{product_id}", name="add_to_cart")
def add_to_cart(
    request: Request,
    product_id: int,
    quantity: int = Form(1),
    variant_sku: str = Form(""),
):
    product = get_product(product_id)
    if not product:
        add_flash(request, "That cap could not be found.", "danger")
        return RedirectResponse(url=str(request.url_for("index")), status_code=303)

    variant = get_variant_for_product(product, variant_sku or None)
    if not variant:
        add_flash(request, "That variant is not available anymore.", "danger")
        return RedirectResponse(url=str(request.url_for("product", product_id=product_id)), status_code=303)

    available_stock = int(variant.get("stock_quantity", 0))
    if available_stock <= 0:
        add_flash(request, f"{product['name']} in {variant.get('color', 'selected style')} is sold out.", "danger")
        return RedirectResponse(url=str(request.url_for("product", product_id=product_id)), status_code=303)

    safe_quantity = max(quantity, 1)
    cart = get_cart(request)
    cart_key = build_cart_key(product_id, variant.get("sku"))
    current_quantity = cart.get(cart_key, 0)
    desired_quantity = min(current_quantity + safe_quantity, available_stock)
    cart[cart_key] = desired_quantity
    save_cart(request, cart)

    if desired_quantity < current_quantity + safe_quantity:
        add_flash(request, f"Only {available_stock} pieces are available for that variant right now.", "info")
    else:
        add_flash(request, f"{product['name']} added to cart.", "success")

    next_page = request.query_params.get("next")
    if next_page == "checkout":
        return RedirectResponse(url=str(request.url_for("checkout")), status_code=303)

    destination = request.headers.get("referer") or str(request.url_for("cart"))
    return RedirectResponse(url=destination, status_code=303)


@router.post("/update_cart/{cart_key}", name="update_cart")
def update_cart(request: Request, cart_key: str, quantity: int = Form(...)):
    cart = get_cart(request)
    if cart_key not in cart:
        add_flash(request, "That cart item could not be found.", "danger")
        return RedirectResponse(url=str(request.url_for("cart")), status_code=303)

    product_id, variant_sku = parse_cart_key(cart_key)
    product = get_product(product_id)
    variant = get_variant_for_product(product, variant_sku) if product else None

    if quantity <= 0:
        cart.pop(cart_key, None)
        add_flash(request, "Item removed from cart.", "info")
    elif not product or not variant:
        cart.pop(cart_key, None)
        add_flash(request, "That cart item is no longer available and was removed.", "danger")
    else:
        available_stock = int(variant.get("stock_quantity", 0))
        cart[cart_key] = min(quantity, available_stock)
        if quantity > available_stock:
            add_flash(request, f"Quantity updated to {available_stock} based on live stock.", "info")
        else:
            add_flash(request, "Cart updated successfully.", "success")

    save_cart(request, cart)
    return RedirectResponse(url=str(request.url_for("cart")), status_code=303)


@router.post("/remove_from_cart/{cart_key}", name="remove_from_cart")
def remove_from_cart(request: Request, cart_key: str):
    cart = get_cart(request)
    cart.pop(cart_key, None)
    save_cart(request, cart)
    add_flash(request, "Item removed from cart.", "info")
    return RedirectResponse(url=str(request.url_for("cart")), status_code=303)
