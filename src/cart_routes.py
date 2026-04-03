from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from src.db import get_product
from src.services import add_flash, build_cart_summary, get_cart, get_current_user, save_cart
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
def add_to_cart(request: Request, product_id: int, quantity: int = Form(1)):
    product = get_product(product_id)
    if not product:
        add_flash(request, "That cap could not be found.", "danger")
        return RedirectResponse(url=str(request.url_for("index")), status_code=303)

    safe_quantity = max(quantity, 1)
    cart = get_cart(request)
    cart[str(product_id)] = cart.get(str(product_id), 0) + safe_quantity
    save_cart(request, cart)
    add_flash(request, f"{product['name']} added to cart.", "success")

    destination = request.headers.get("referer") or str(request.url_for("cart"))
    return RedirectResponse(url=destination, status_code=303)


@router.post("/update_cart/{product_id}", name="update_cart")
def update_cart(request: Request, product_id: int, quantity: int = Form(...)):
    cart = get_cart(request)
    if quantity > 0:
        cart[str(product_id)] = quantity
        add_flash(request, "Cart updated successfully.", "success")
    else:
        cart.pop(str(product_id), None)
        add_flash(request, "Item removed from cart.", "info")

    save_cart(request, cart)
    return RedirectResponse(url=str(request.url_for("cart")), status_code=303)


@router.post("/remove_from_cart/{product_id}", name="remove_from_cart")
def remove_from_cart(request: Request, product_id: int):
    cart = get_cart(request)
    cart.pop(str(product_id), None)
    save_cart(request, cart)
    add_flash(request, "Item removed from cart.", "info")
    return RedirectResponse(url=str(request.url_for("cart")), status_code=303)
