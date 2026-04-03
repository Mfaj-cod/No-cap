from typing import Any

from fastapi import Request

from src.data import WHOLESALE_DISCOUNT, WHOLESALE_THRESHOLD
from src.db import format_variant_label, get_product, get_user_by_id, get_variant_for_product

GUEST_USER_ID = 0
CART_KEY_SEPARATOR = "__"
CHECKOUT_SESSION_KEY = "checkout_data"


def add_flash(request: Request, message: str, category: str = "info") -> None:
    flashes = request.session.get("_flash_messages", [])
    flashes.append({"category": category, "message": message})
    request.session["_flash_messages"] = flashes


def pop_flash_messages(request: Request) -> list[dict[str, str]]:
    messages = request.session.get("_flash_messages", [])
    request.session["_flash_messages"] = []
    return messages


def get_current_user(request: Request) -> dict[str, Any] | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return get_user_by_id(int(user_id))


def login_user(request: Request, user: dict[str, Any]) -> None:
    request.session["user_id"] = user["id"]


def logout_user(request: Request) -> None:
    request.session.pop("user_id", None)


def build_cart_key(product_id: int, variant_sku: str | None) -> str:
    return f"{product_id}{CART_KEY_SEPARATOR}{variant_sku or 'default'}"


def parse_cart_key(cart_key: str) -> tuple[int, str | None]:
    if CART_KEY_SEPARATOR not in cart_key:
        return int(cart_key), None
    product_id, variant_sku = cart_key.split(CART_KEY_SEPARATOR, 1)
    return int(product_id), variant_sku if variant_sku != "default" else None


def get_cart(request: Request) -> dict[str, int]:
    cart = request.session.get("cart", {})
    return {str(cart_key): int(quantity) for cart_key, quantity in cart.items()}


def save_cart(request: Request, cart: dict[str, int]) -> None:
    request.session["cart"] = cart


def clear_cart(request: Request) -> None:
    request.session["cart"] = {}


def remember_checkout_data(request: Request, checkout_data: dict[str, str]) -> None:
    request.session[CHECKOUT_SESSION_KEY] = {
        "name": checkout_data.get("name", "").strip(),
        "email": checkout_data.get("email", "").strip().lower(),
        "phone": checkout_data.get("phone", "").strip(),
        "address": checkout_data.get("address", "").strip(),
        "city": checkout_data.get("city", "").strip(),
        "state": checkout_data.get("state", "").strip(),
        "pincode": checkout_data.get("pincode", "").strip(),
        "payment_method": checkout_data.get("payment_method", "cod").strip(),
    }


def get_saved_checkout_data(request: Request) -> dict[str, str]:
    saved_data = request.session.get(CHECKOUT_SESSION_KEY, {})
    return {
        "name": str(saved_data.get("name", "")),
        "email": str(saved_data.get("email", "")),
        "phone": str(saved_data.get("phone", "")),
        "address": str(saved_data.get("address", "")),
        "city": str(saved_data.get("city", "")),
        "state": str(saved_data.get("state", "")),
        "pincode": str(saved_data.get("pincode", "")),
        "payment_method": str(saved_data.get("payment_method", "cod")),
    }


def clear_saved_checkout_data(request: Request) -> None:
    request.session.pop(CHECKOUT_SESSION_KEY, None)


def remember_guest_order(request: Request, order_id: int) -> None:
    guest_order_ids = request.session.get("guest_order_ids", [])
    if order_id not in guest_order_ids:
        guest_order_ids.append(order_id)
        request.session["guest_order_ids"] = guest_order_ids


def can_access_order(request: Request, order: dict[str, Any] | None) -> bool:
    if not order:
        return False

    current_user = get_current_user(request)
    if current_user and order["user_id"] == current_user["id"]:
        return True

    return order["user_id"] == GUEST_USER_ID and order["id"] in request.session.get("guest_order_ids", [])


def cart_item_count(request: Request) -> int:
    return sum(get_cart(request).values())


def build_cart_summary(request: Request, user: dict[str, Any] | None = None) -> dict[str, Any]:
    cart = get_cart(request)
    buyer_role = user["role"] if user else "customer"
    items: list[dict[str, Any]] = []
    total_quantity = 0

    for cart_key, quantity in cart.items():
        product_id, variant_sku = parse_cart_key(cart_key)
        product = get_product(product_id)
        if not product:
            continue

        variant = get_variant_for_product(product, variant_sku)
        if not variant:
            continue

        available_stock = int(variant.get("stock_quantity", 0))
        effective_quantity = min(int(quantity), available_stock)
        if effective_quantity <= 0:
            continue

        total_quantity += effective_quantity
        items.append(
            {
                "cart_key": build_cart_key(product_id, variant.get("sku")),
                "product": product,
                "variant": variant,
                "variant_label": format_variant_label(variant),
                "quantity": effective_quantity,
                "available_stock": available_stock,
                "retail_unit_price": product["normal_price"],
                "wholesale_unit_price": product["shop_owner_price"],
            }
        )

    wholesale_eligible = buyer_role == "shop_owner" and total_quantity >= WHOLESALE_THRESHOLD
    retail_subtotal = 0.0
    final_total = 0.0

    for item in items:
        item["applied_unit_price"] = item["wholesale_unit_price"] if wholesale_eligible else item["retail_unit_price"]
        item["line_total"] = round(item["applied_unit_price"] * item["quantity"], 2)
        item["retail_line_total"] = round(item["retail_unit_price"] * item["quantity"], 2)
        retail_subtotal += item["retail_line_total"]
        final_total += item["line_total"]

    discount_amount = round(retail_subtotal - final_total, 2)
    pricing_tier = "shop_owner" if wholesale_eligible else "retail"

    return {
        "items": items,
        "buyer_role": buyer_role,
        "total_quantity": total_quantity,
        "retail_subtotal": round(retail_subtotal, 2),
        "discount_amount": discount_amount,
        "final_total": round(final_total, 2),
        "pricing_tier": pricing_tier,
        "wholesale_eligible": wholesale_eligible,
        "wholesale_threshold": WHOLESALE_THRESHOLD,
        "wholesale_discount_percent": int(WHOLESALE_DISCOUNT * 100),
        "remaining_to_wholesale": max(WHOLESALE_THRESHOLD - total_quantity, 0),
    }

