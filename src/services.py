from typing import Any

from fastapi import Request

from src.data import WHOLESALE_DISCOUNT, WHOLESALE_THRESHOLD
from src.db import get_product, get_user_by_id


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


def get_cart(request: Request) -> dict[str, int]:
    cart = request.session.get("cart", {})
    return {str(product_id): int(quantity) for product_id, quantity in cart.items()}


def save_cart(request: Request, cart: dict[str, int]) -> None:
    request.session["cart"] = cart


def clear_cart(request: Request) -> None:
    request.session["cart"] = {}


def cart_item_count(request: Request) -> int:
    return sum(get_cart(request).values())


def build_cart_summary(request: Request, user: dict[str, Any] | None = None) -> dict[str, Any]:
    cart = get_cart(request)
    buyer_role = user["role"] if user else "customer"
    items: list[dict[str, Any]] = []
    total_quantity = 0

    for product_id, quantity in cart.items():
        product = get_product(int(product_id))
        if not product:
            continue

        total_quantity += quantity
        items.append(
            {
                "product": product,
                "quantity": quantity,
                "retail_unit_price": product["normal_price"],
                "wholesale_unit_price": product["shop_owner_price"],
            }
        )

    wholesale_eligible = buyer_role == "shop_owner" and total_quantity >= WHOLESALE_THRESHOLD
    discount_multiplier = 1 - WHOLESALE_DISCOUNT
    retail_subtotal = 0.0
    final_total = 0.0

    for item in items:
        item["applied_unit_price"] = (
            round(item["retail_unit_price"] * discount_multiplier, 2)
            if wholesale_eligible
            else item["retail_unit_price"]
        )
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
        "remaining_to_wholesale": max(WHOLESALE_THRESHOLD - total_quantity, 0),
    }
