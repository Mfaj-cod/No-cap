import razorpay
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from src.config import settings
from src.db import attach_razorpay_order, create_order, get_order, mark_order_paid, update_order_status
from src.services import add_flash, build_cart_summary, clear_cart, get_current_user
from src.web import render_template

router = APIRouter()

client = (
    razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))
    if settings.razorpay_key_id and settings.razorpay_key_secret
    else None
)


def _redirect(request: Request, route_name: str):
    return RedirectResponse(url=str(request.url_for(route_name)), status_code=303)


@router.get("/checkout", response_class=HTMLResponse, name="checkout")
def checkout_page(request: Request):
    current_user = get_current_user(request)
    if not current_user:
        add_flash(request, "Please log in before checkout.", "info")
        return _redirect(request, "login")

    cart_summary = build_cart_summary(request, current_user)
    if not cart_summary["items"]:
        add_flash(request, "Your cart is empty.", "info")
        return _redirect(request, "cart")

    return render_template(
        request,
        "checkout.html",
        cart_summary=cart_summary,
        checkout_defaults={"name": current_user["name"], "email": current_user["email"]},
        razorpay_order=None,
        pending_order_id=None,
        razorpay_key_id=settings.razorpay_key_id,
        checkout_phone="",
        checkout_address="",
        checkout_city="",
        checkout_state="",
        checkout_pincode="",
        selected_payment_method="cod",
    )


@router.post("/checkout", name="place_order")
def place_order(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    pincode: str = Form(...),
    payment_method: str = Form(...),
):
    current_user = get_current_user(request)
    if not current_user:
        add_flash(request, "Please log in before checkout.", "info")
        return _redirect(request, "login")

    cart_summary = build_cart_summary(request, current_user)
    if not cart_summary["items"]:
        add_flash(request, "Your cart is empty.", "info")
        return _redirect(request, "cart")

    if payment_method not in {"cod", "upi", "card"}:
        add_flash(request, "Please choose a valid payment method.", "danger")
        return _redirect(request, "checkout")

    if payment_method in {"upi", "card"} and client is None:
        add_flash(request, "Online payments are not configured right now. Please use Cash on Delivery.", "danger")
        return _redirect(request, "checkout")

    checkout_data = {
        "name": name.strip(),
        "email": email.strip().lower(),
        "phone": phone.strip(),
        "address": address.strip(),
        "city": city.strip(),
        "state": state.strip(),
        "pincode": pincode.strip(),
        "payment_method": payment_method,
    }

    order_id = create_order(current_user["id"], checkout_data, cart_summary)

    if payment_method == "cod":
        update_order_status(order_id, "confirmed")
        clear_cart(request)
        add_flash(request, "Your order has been placed successfully.", "success")
        success_url = request.url_for("success_page").include_query_params(order_id=order_id)
        return RedirectResponse(url=str(success_url), status_code=303)

    razorpay_order = client.order.create(
        {
            "amount": int(round(cart_summary["final_total"] * 100)),
            "currency": "INR",
            "receipt": str(order_id),
        }
    )
    attach_razorpay_order(order_id, razorpay_order["id"])
    add_flash(request, "Complete the Razorpay payment to finish your order.", "info")

    return render_template(
        request,
        "checkout.html",
        cart_summary=cart_summary,
        checkout_defaults={"name": name, "email": email},
        razorpay_order=razorpay_order,
        pending_order_id=order_id,
        razorpay_key_id=settings.razorpay_key_id,
        checkout_phone=phone,
        checkout_address=address,
        checkout_city=city,
        checkout_state=state,
        checkout_pincode=pincode,
        selected_payment_method=payment_method,
    )


@router.post("/success", name="payment_success")
def payment_success(
    request: Request,
    order_id: int = Form(...),
    razorpay_payment_id: str = Form(""),
):
    current_user = get_current_user(request)
    if not current_user:
        add_flash(request, "Please log in to finish viewing your order.", "info")
        return _redirect(request, "login")

    order = get_order(order_id)
    if not order or order["user_id"] != current_user["id"]:
        add_flash(request, "That order could not be found in your account.", "danger")
        return _redirect(request, "account")

    mark_order_paid(order_id, razorpay_payment_id or "manual-confirmation")
    clear_cart(request)
    add_flash(request, "Payment received successfully.", "success")
    success_url = request.url_for("success_page").include_query_params(order_id=order_id)
    return RedirectResponse(url=str(success_url), status_code=303)


@router.get("/success", response_class=HTMLResponse, name="success_page")
def success_page(request: Request, order_id: int):
    current_user = get_current_user(request)
    if not current_user:
        add_flash(request, "Please log in to view your order.", "info")
        return _redirect(request, "login")

    order = get_order(order_id)
    if not order or order["user_id"] != current_user["id"]:
        add_flash(request, "That order could not be found in your account.", "danger")
        return _redirect(request, "account")

    return render_template(request, "success.html", order=order)


@router.get("/failure", response_class=HTMLResponse, name="failure")
def failure_page(request: Request, order_id: int | None = None):
    return render_template(request, "failure.html", order_id=order_id)
