import logging
import sys
import razorpay
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from src.config import settings

logger = logging.getLogger(__name__)
from src.db import (
    attach_razorpay_order,
    cancel_order_and_restore_stock,
    create_order,
    get_order,
    get_recent_order_activity,
    mark_order_paid,
    update_order_status,
)
from src.notifications import send_order_placed_email
from src.services import (
    GUEST_USER_ID,
    add_flash,
    build_cart_summary,
    can_access_order,
    clear_cart,
    clear_saved_checkout_data,
    get_current_user,
    get_saved_checkout_data,
    remember_checkout_data,
    remember_guest_order,
)
from src.web import render_template

router = APIRouter()

ONLINE_PAYMENT_METHODS = {"upi", "card", "wallet"}
PAYMENT_METHOD_LABELS = {
    "cod": "Cash on Delivery",
    "upi": "UPI via Razorpay",
    "card": "Credit or Debit Card via Razorpay",
    "wallet": "Wallet via Razorpay",
}

client = (
    razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))
    if settings.razorpay_key_id and settings.razorpay_key_secret
    else None
)

# Debug: Show client initialization status
if client:
    print(f"[DEBUG] Razorpay client initialized with key: {settings.razorpay_key_id}\n")
else:
    print(f"[DEBUG] Razorpay client is None. Key ID set: {bool(settings.razorpay_key_id)}, Key Secret set: {bool(settings.razorpay_key_secret)}\n")


def _redirect(request: Request, route_name: str):
    return RedirectResponse(url=str(request.url_for(route_name)), status_code=303)


def _checkout_url(request: Request, payment_method: str | None = None) -> str:
    url = request.url_for("checkout")
    if payment_method:
        url = url.include_query_params(payment_method=payment_method)
    return str(url)


def _render_checkout(
    request: Request,
    current_user: dict | None,
    cart_summary: dict,
    razorpay_order: dict | None = None,
    pending_order_id: int | None = None,
    selected_payment_method: str | None = None,
):
    saved_checkout = get_saved_checkout_data(request)
    payment_method = (
        selected_payment_method
        or request.query_params.get("payment_method")
        or saved_checkout.get("payment_method")
        or "cod"
    )
    if payment_method not in PAYMENT_METHOD_LABELS:
        payment_method = "cod"
    if payment_method in ONLINE_PAYMENT_METHODS and client is None:
        payment_method = "cod"

    return render_template(
        request,
        "checkout.html",
        cart_summary=cart_summary,
        checkout_defaults={
            "name": saved_checkout.get("name") or (current_user["name"] if current_user else ""),
            "email": saved_checkout.get("email") or (current_user["email"] if current_user else ""),
        },
        guest_checkout=not bool(current_user),
        razorpay_order=razorpay_order,
        pending_order_id=pending_order_id,
        razorpay_key_id=settings.razorpay_key_id,
        checkout_phone=saved_checkout.get("phone", ""),
        checkout_address=saved_checkout.get("address", ""),
        checkout_city=saved_checkout.get("city", ""),
        checkout_state=saved_checkout.get("state", ""),
        checkout_pincode=saved_checkout.get("pincode", ""),
        selected_payment_method=payment_method,
        online_payments_available=client is not None,
    )


def _checkout_risk_message(checkout_data: dict[str, str], payment_method: str) -> str | None:
    activity = get_recent_order_activity(
        checkout_data["email"],
        checkout_data["phone"],
        checkout_data["address"],
        checkout_data["pincode"],
    )

    if activity["recent_attempts"] >= 10:
        return (
            "We paused checkout for a few minutes because several recent orders were attempted "
            "with the same contact or address. Please wait a bit, then try again."
        )

    if payment_method in ONLINE_PAYMENT_METHODS and activity["recent_cancelled"] >= 5:
        return (
            "We noticed multiple incomplete online payment attempts recently. Please wait a few minutes "
            "before retrying, or switch to Cash on Delivery if you need to place the order now."
        )

    if activity["distinct_emails_for_phone"] >= 5 or activity["distinct_phones_for_email"] >= 5:
        return (
            "We could not verify this payment pattern right now. Please use one consistent email and phone number, "
            "or contact support if you need help placing the order."
        )

    return None


@router.get("/checkout", response_class=HTMLResponse, name="checkout")
def checkout_page(request: Request):
    current_user = get_current_user(request)
    cart_summary = build_cart_summary(request, current_user)
    if not cart_summary["items"]:
        add_flash(request, "Your cart is empty.", "info")
        return _redirect(request, "cart")

    return _render_checkout(request, current_user, cart_summary)


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
    cart_summary = build_cart_summary(request, current_user)
    if not cart_summary["items"]:
        add_flash(request, "Your cart is empty.", "info")
        return _redirect(request, "cart")

    if payment_method not in PAYMENT_METHOD_LABELS:
        add_flash(request, "Please choose a valid payment method.", "danger")
        return RedirectResponse(url=_checkout_url(request), status_code=303)

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
    remember_checkout_data(request, checkout_data)

    if payment_method in ONLINE_PAYMENT_METHODS and client is None:
        add_flash(request, "Online payments are not configured right now. Please use Cash on Delivery.", "danger")
        return RedirectResponse(url=_checkout_url(request, "cod"), status_code=303)

    risk_message = _checkout_risk_message(checkout_data, payment_method)
    if risk_message:
        add_flash(request, risk_message, "danger")
        return RedirectResponse(url=_checkout_url(request, payment_method), status_code=303)

    try:
        order_id = create_order(current_user["id"] if current_user else GUEST_USER_ID, checkout_data, cart_summary)
    except ValueError as exc:
        add_flash(request, str(exc), "danger")
        return _redirect(request, "cart")

    if not current_user:
        remember_guest_order(request, order_id)

    if payment_method == "cod":
        update_order_status(order_id, "confirmed")
        try:
            send_order_placed_email(order_id)
        except Exception:
            pass
        clear_cart(request)
        clear_saved_checkout_data(request)
        add_flash(request, "Your order has been placed successfully.", "success")
        success_url = request.url_for("success_page").include_query_params(order_id=order_id)
        return RedirectResponse(url=str(success_url), status_code=303)

    try:
        print(f"[DEBUG] About to create Razorpay order. Client: {client is not None}, Amount: {int(round(cart_summary['final_total'] * 100))}\n", flush=True)

        amount = int(round(float(cart_summary["final_total"]) * 100))

        print("Creating Razorpay order with amount:", amount, flush=True)

        razorpay_order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "receipt": str(order_id),
        })

        print("Razorpay order success:", razorpay_order, flush=True)

    except Exception as e:
        print(f"[ERROR] Razorpay order creation failed!\n")
        print(f"[ERROR] Exception type: {type(e).__name__}\n")
        print(f"[ERROR] Exception message: {str(e)}\n")
        sys.stderr.flush()
        logger.error(f"Razorpay order creation failed: {str(e)}", exc_info=True)
        cancel_order_and_restore_stock(order_id)
        add_flash(
            request,
            "We could not start the online payment right now. Your cart is still ready, so you can retry or switch to Cash on Delivery.",
            "danger",
        )
        return RedirectResponse(url=_checkout_url(request, "cod"), status_code=303)

    attach_razorpay_order(order_id, razorpay_order["id"])
    add_flash(request, "Complete the Razorpay payment to finish your order. Retry is enabled if the first attempt fails.", "info")

    return _render_checkout(
        request,
        current_user,
        build_cart_summary(request, current_user),
        razorpay_order=razorpay_order,
        pending_order_id=order_id,
        selected_payment_method=payment_method,
    )


@router.post("/success", name="payment_success")
def payment_success(
    request: Request,
    order_id: int = Form(...),
    razorpay_payment_id: str = Form(""),
    razorpay_order_id: str = Form(""),
    razorpay_signature: str = Form(""),
):
    order = get_order(order_id)
    if not can_access_order(request, order):
        add_flash(request, "That order could not be found.", "danger")
        return _redirect(request, "checkout")

    success_url = request.url_for("success_page").include_query_params(order_id=order_id)
    failure_url = request.url_for("failure").include_query_params(
        order_id=order_id,
        payment_method=order["payment_method"],
    )

    if order["status"] in {"paid", "confirmed"}:
        clear_cart(request)
        clear_saved_checkout_data(request)
        return RedirectResponse(url=str(success_url), status_code=303)

    if order["payment_method"] not in ONLINE_PAYMENT_METHODS:
        return RedirectResponse(url=str(success_url), status_code=303)

    if order["status"] != "pending":
        add_flash(request, "This order is no longer awaiting payment.", "info")
        return RedirectResponse(url=str(success_url), status_code=303)

    if client is None or not razorpay_payment_id or not razorpay_order_id or not razorpay_signature:
        cancel_order_and_restore_stock(order_id)
        add_flash(request, "We could not confirm that payment. Please retry or switch to Cash on Delivery.", "danger")
        return RedirectResponse(url=str(failure_url), status_code=303)

    if order.get("razorpay_order_id") != razorpay_order_id:
        cancel_order_and_restore_stock(order_id)
        add_flash(request, "The payment reference did not match this order. Please try again.", "danger")
        return RedirectResponse(url=str(failure_url), status_code=303)

    try:
        client.utility.verify_payment_signature(
            {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            }
        )
    except Exception:
        cancel_order_and_restore_stock(order_id)
        add_flash(request, "We could not verify that payment. Please retry or switch to Cash on Delivery.", "danger")
        return RedirectResponse(url=str(failure_url), status_code=303)

    mark_order_paid(order_id, razorpay_payment_id)
    try:
        send_order_placed_email(order_id)
    except Exception:
        pass
    clear_cart(request)
    clear_saved_checkout_data(request)
    add_flash(request, "Payment received successfully.", "success")
    return RedirectResponse(url=str(success_url), status_code=303)


@router.get("/success", response_class=HTMLResponse, name="success_page")
def success_page(request: Request, order_id: int):
    order = get_order(order_id)
    if not can_access_order(request, order):
        add_flash(request, "That order could not be found.", "danger")
        return _redirect(request, "checkout")

    return render_template(request, "success.html", order=order)


@router.get("/failure", response_class=HTMLResponse, name="failure")
def failure_page(request: Request, order_id: int | None = None, payment_method: str | None = None):
    retry_payment_method = payment_method if payment_method in ONLINE_PAYMENT_METHODS else "upi"

    if order_id:
        order = get_order(order_id)
        if order and not can_access_order(request, order):
            add_flash(request, "That order could not be found.", "danger")
            return _redirect(request, "checkout")

        if order and order.get("payment_method") in ONLINE_PAYMENT_METHODS:
            retry_payment_method = order["payment_method"]

        if order and cancel_order_and_restore_stock(order_id):
            add_flash(request, "Payment was not completed. Reserved stock has been released and your cart is still saved.", "info")

    return render_template(
        request,
        "failure.html",
        order_id=order_id,
        retry_payment_method=retry_payment_method,
        retry_payment_label=PAYMENT_METHOD_LABELS.get(retry_payment_method, "online payment"),
    )

