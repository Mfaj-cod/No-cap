import json
import sqlite3
from typing import Any

from src.config import settings
from src.data import CATEGORIES, PRODUCTS, WHOLESALE_DISCOUNT

DB_SCHEMA_VERSION = 4


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(settings.database_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_database() -> None:
    connection = get_connection()
    version = connection.execute("PRAGMA user_version").fetchone()[0]

    if version != DB_SCHEMA_VERSION:
        _reset_database(connection)
        connection.execute(f"PRAGMA user_version = {DB_SCHEMA_VERSION}")

    _seed_reference_data(connection)
    connection.commit()
    connection.close()


def _reset_database(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('customer', 'shop_owner', 'admin')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            image_url TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            normal_price REAL NOT NULL,
            image_url TEXT NOT NULL,
            category TEXT NOT NULL,
            details TEXT NOT NULL,
            attributes TEXT NOT NULL,
            media_gallery TEXT NOT NULL,
            variants TEXT NOT NULL,
            reviews TEXT NOT NULL,
            featured INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            pincode TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            total REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            buyer_role TEXT NOT NULL,
            total_quantity INTEGER NOT NULL,
            pricing_tier TEXT NOT NULL,
            discount_amount REAL NOT NULL DEFAULT 0,
            razorpay_order_id TEXT,
            razorpay_payment_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            variant_sku TEXT NOT NULL,
            variant_label TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            retail_unit_price REAL NOT NULL,
            wholesale_unit_price REAL NOT NULL,
            applied_unit_price REAL NOT NULL,
            line_total REAL NOT NULL,
            FOREIGN KEY(order_id) REFERENCES orders(id)
        );

        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )


def _find_variant_by_sku(variants: list[dict[str, Any]], variant_sku: str | None) -> dict[str, Any] | None:
    if variant_sku:
        for variant in variants:
            if variant.get("sku") == variant_sku:
                return variant
    for variant in variants:
        if int(variant.get("stock_quantity", 0)) > 0:
            return variant
    return variants[0] if variants else None


def format_variant_label(variant: dict[str, Any] | None) -> str:
    if not variant:
        return "Default"
    parts = [variant.get("color"), variant.get("size")]
    return " / ".join(part for part in parts if part)


def get_variant_for_product(product: dict[str, Any], variant_sku: str | None = None) -> dict[str, Any] | None:
    return _find_variant_by_sku(product.get("variants", []), variant_sku)


def _seed_reference_data(connection: sqlite3.Connection) -> None:
    connection.executemany(
        "INSERT OR REPLACE INTO categories (name, image_url) VALUES (?, ?)",
        [(category["name"], category["image_url"]) for category in CATEGORIES],
    )
    connection.executemany(
        """
        INSERT OR REPLACE INTO products
            (
                id, name, description, normal_price, image_url, category,
                details, attributes, media_gallery, variants, reviews, featured
            )
        VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                product.get("id"),
                product.get("name"),
                product.get("description"),
                product.get("normal_price"),
                product.get("image_url"),
                product.get("category"),
                json.dumps(product.get("details", [])),
                json.dumps(product.get("attributes", {})),
                json.dumps(product.get("media_gallery", [product.get("image_url")]) ),
                json.dumps(product.get("variants", [])),
                json.dumps(product.get("reviews", [])),
                1 if product.get("featured") else 0,
            )
            for product in PRODUCTS
        ],
    )


def _product_from_row(row: sqlite3.Row) -> dict[str, Any]:
    normal_price = float(row["normal_price"])
    reviews = json.loads(row["reviews"]) if row["reviews"] else []
    ratings = [review["rating"] for review in reviews if isinstance(review, dict) and "rating" in review]
    attributes = json.loads(row["attributes"]) if row["attributes"] else {}
    media_gallery = json.loads(row["media_gallery"]) if row["media_gallery"] else []
    variants = json.loads(row["variants"]) if row["variants"] else []
    total_stock = sum(max(int(variant.get("stock_quantity", 0)), 0) for variant in variants)
    default_variant = _find_variant_by_sku(variants, None)
    shop_owner_price = round(normal_price * (1 - WHOLESALE_DISCOUNT), 2)

    if not media_gallery:
        media_gallery = [row["image_url"]]

    return {
        "id": row["id"],
        "name": row["name"],
        "description": row["description"],
        "normal_price": normal_price,
        "shop_owner_price": shop_owner_price,
        "image_url": row["image_url"],
        "media_gallery": media_gallery,
        "category": row["category"],
        "details": json.loads(row["details"]) if row["details"] else [],
        "attributes": attributes,
        "variants": variants,
        "default_variant": default_variant,
        "variant_count": len(variants),
        "total_stock": total_stock,
        "in_stock": total_stock > 0,
        "available_colors": sorted({variant.get("color") for variant in variants if variant.get("color")}),
        "reviews": reviews,
        "review_count": len(reviews),
        "average_rating": round(sum(ratings) / len(ratings), 1) if ratings else None,
        "featured": bool(row["featured"]),
    }


def list_categories() -> list[dict[str, Any]]:
    connection = get_connection()
    rows = connection.execute(
        "SELECT name, image_url FROM categories ORDER BY name"
    ).fetchall()
    connection.close()
    return [{"name": row["name"], "image_url": row["image_url"]} for row in rows]


def list_products(category: str | None = None, featured_only: bool = False) -> list[dict[str, Any]]:
    query = """
        SELECT id, name, description, normal_price, image_url, category,
               details, attributes, media_gallery, variants, reviews, featured
        FROM products
    """
    conditions = []
    parameters: list[Any] = []

    if category:
        conditions.append("category = ?")
        parameters.append(category)

    if featured_only:
        conditions.append("featured = 1")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY featured DESC, id"

    connection = get_connection()
    rows = connection.execute(query, parameters).fetchall()
    connection.close()
    return [_product_from_row(row) for row in rows]


def get_product(product_id: int) -> dict[str, Any] | None:
    connection = get_connection()
    row = connection.execute(
        """
        SELECT id, name, description, normal_price, image_url, category,
               details, attributes, media_gallery, variants, reviews, featured
        FROM products
        WHERE id = ?
        """,
        (product_id,),
    ).fetchone()
    connection.close()
    return _product_from_row(row) if row else None


def get_user_by_email(email: str) -> dict[str, Any] | None:
    connection = get_connection()
    row = connection.execute(
        "SELECT id, name, email, password_hash, role, created_at FROM users WHERE lower(email) = lower(?)",
        (email,),
    ).fetchone()
    connection.close()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    connection = get_connection()
    row = connection.execute(
        "SELECT id, name, email, password_hash, role, created_at FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    connection.close()
    return dict(row) if row else None


def create_user(name: str, email: str, password_hash: str, role: str) -> None:
    connection = get_connection()
    try:
        connection.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
            (name.strip(), email.strip().lower(), password_hash, role),
        )
        connection.commit()
    finally:
        connection.close()


def create_subscription(email: str) -> bool:
    connection = get_connection()
    try:
        connection.execute(
            "INSERT INTO subscriptions (email) VALUES (?)",
            (email.strip().lower(),),
        )
        connection.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        connection.close()


def create_order(
    user_id: int,
    checkout_data: dict[str, str],
    cart_summary: dict[str, Any],
) -> int:
    connection = get_connection()
    cursor = connection.cursor()

    try:
        reserved_variants: list[tuple[int, list[dict[str, Any]]]] = []
        for item in cart_summary["items"]:
            row = cursor.execute(
                "SELECT name, variants FROM products WHERE id = ?",
                (item["product"]["id"],),
            ).fetchone()
            if not row:
                raise ValueError(f"{item['product']['name']} is no longer available.")

            variants = json.loads(row["variants"]) if row["variants"] else []
            variant = _find_variant_by_sku(variants, item["variant"]["sku"])
            if not variant:
                raise ValueError(f"The selected variant for {row['name']} is no longer available.")

            available_stock = int(variant.get("stock_quantity", 0))
            if available_stock < item["quantity"]:
                raise ValueError(
                    f"Only {available_stock} left for {row['name']} ({format_variant_label(variant)})."
                )

            variant["stock_quantity"] = available_stock - item["quantity"]
            reserved_variants.append((item["product"]["id"], variants))

        cursor.execute(
            """
            INSERT INTO orders
                (
                    user_id, name, email, phone, address, city, state, pincode,
                    payment_method, total, status, buyer_role, total_quantity,
                    pricing_tier, discount_amount
                )
            VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                checkout_data["name"],
                checkout_data["email"],
                checkout_data["phone"],
                checkout_data["address"],
                checkout_data["city"],
                checkout_data["state"],
                checkout_data["pincode"],
                checkout_data["payment_method"],
                cart_summary["final_total"],
                "pending",
                cart_summary["buyer_role"],
                cart_summary["total_quantity"],
                cart_summary["pricing_tier"],
                cart_summary["discount_amount"],
            ),
        )

        order_id = cursor.lastrowid
        for item in cart_summary["items"]:
            cursor.execute(
                """
                INSERT INTO order_items
                    (
                        order_id, product_id, product_name, variant_sku, variant_label,
                        quantity, retail_unit_price, wholesale_unit_price,
                        applied_unit_price, line_total
                    )
                VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    order_id,
                    item["product"]["id"],
                    item["product"]["name"],
                    item["variant"]["sku"],
                    item["variant_label"],
                    item["quantity"],
                    item["retail_unit_price"],
                    item["wholesale_unit_price"],
                    item["applied_unit_price"],
                    item["line_total"],
                ),
            )

        for product_id, updated_variants in reserved_variants:
            cursor.execute(
                "UPDATE products SET variants = ? WHERE id = ?",
                (json.dumps(updated_variants), product_id),
            )

        connection.commit()
        return order_id
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def attach_razorpay_order(order_id: int, razorpay_order_id: str) -> None:
    connection = get_connection()
    connection.execute(
        "UPDATE orders SET razorpay_order_id = ? WHERE id = ?",
        (razorpay_order_id, order_id),
    )
    connection.commit()
    connection.close()


def update_order_status(order_id: int, status: str) -> None:
    connection = get_connection()
    connection.execute(
        "UPDATE orders SET status = ? WHERE id = ?",
        (status, order_id),
    )
    connection.commit()
    connection.close()


def mark_order_paid(order_id: int, payment_id: str) -> None:
    connection = get_connection()
    connection.execute(
        "UPDATE orders SET status = ?, razorpay_payment_id = ? WHERE id = ?",
        ("paid", payment_id, order_id),
    )
    connection.commit()
    connection.close()


def cancel_order_and_restore_stock(order_id: int) -> bool:
    connection = get_connection()
    cursor = connection.cursor()
    order = cursor.execute(
        "SELECT status FROM orders WHERE id = ?",
        (order_id,),
    ).fetchone()

    if not order or order["status"] != "pending":
        connection.close()
        return False

    items = cursor.execute(
        "SELECT product_id, quantity, variant_sku FROM order_items WHERE order_id = ?",
        (order_id,),
    ).fetchall()

    try:
        for item in items:
            row = cursor.execute(
                "SELECT variants FROM products WHERE id = ?",
                (item["product_id"],),
            ).fetchone()
            if not row:
                continue
            variants = json.loads(row["variants"]) if row["variants"] else []
            variant = _find_variant_by_sku(variants, item["variant_sku"])
            if variant:
                variant["stock_quantity"] = int(variant.get("stock_quantity", 0)) + int(item["quantity"])
                cursor.execute(
                    "UPDATE products SET variants = ? WHERE id = ?",
                    (json.dumps(variants), item["product_id"]),
                )

        cursor.execute(
            "UPDATE orders SET status = ? WHERE id = ?",
            ("cancelled", order_id),
        )
        connection.commit()
        return True
    finally:
        connection.close()



def get_recent_order_activity(email: str, phone: str, address: str, pincode: str, minutes: int = 30) -> dict[str, int]:
    normalized_email = email.strip().lower()
    normalized_phone = phone.strip()
    normalized_address = address.strip().lower()
    normalized_pincode = pincode.strip()
    window = f"-{minutes} minutes"

    connection = get_connection()
    activity_row = connection.execute(
        """
        SELECT COUNT(*) AS recent_attempts,
               SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS recent_cancelled,
               SUM(CASE WHEN lower(email) = ? THEN 1 ELSE 0 END) AS recent_email_matches,
               SUM(CASE WHEN phone = ? THEN 1 ELSE 0 END) AS recent_phone_matches,
               SUM(CASE WHEN lower(trim(address)) = ? AND pincode = ? THEN 1 ELSE 0 END) AS recent_address_matches
        FROM orders
        WHERE created_at >= datetime('now', ?)
          AND (
              lower(email) = ?
              OR phone = ?
              OR (lower(trim(address)) = ? AND pincode = ?)
          )
        """,
        (
            normalized_email,
            normalized_phone,
            normalized_address,
            normalized_pincode,
            window,
            normalized_email,
            normalized_phone,
            normalized_address,
            normalized_pincode,
        ),
    ).fetchone()

    distinct_email_row = connection.execute(
        """
        SELECT COUNT(DISTINCT lower(email)) AS distinct_emails_for_phone
        FROM orders
        WHERE created_at >= datetime('now', ?) AND phone = ?
        """,
        (window, normalized_phone),
    ).fetchone()

    distinct_phone_row = connection.execute(
        """
        SELECT COUNT(DISTINCT phone) AS distinct_phones_for_email
        FROM orders
        WHERE created_at >= datetime('now', ?) AND lower(email) = ?
        """,
        (window, normalized_email),
    ).fetchone()
    connection.close()

    return {
        "recent_attempts": int(activity_row["recent_attempts"] or 0),
        "recent_cancelled": int(activity_row["recent_cancelled"] or 0),
        "recent_email_matches": int(activity_row["recent_email_matches"] or 0),
        "recent_phone_matches": int(activity_row["recent_phone_matches"] or 0),
        "recent_address_matches": int(activity_row["recent_address_matches"] or 0),
        "distinct_emails_for_phone": int(distinct_email_row["distinct_emails_for_phone"] or 0),
        "distinct_phones_for_email": int(distinct_phone_row["distinct_phones_for_email"] or 0),
    }

def list_orders_for_user(user_id: int) -> list[dict[str, Any]]:
    connection = get_connection()
    rows = connection.execute(
        """
        SELECT id, total, status, buyer_role, total_quantity, pricing_tier, discount_amount,
               payment_method, created_at
        FROM orders
        WHERE user_id = ?
        ORDER BY created_at DESC, id DESC
        """,
        (user_id,),
    ).fetchall()
    connection.close()
    return [dict(row) for row in rows]


def get_order(order_id: int) -> dict[str, Any] | None:
    connection = get_connection()
    row = connection.execute(
        """
        SELECT id, user_id, name, email, phone, address, city, state, pincode,
               payment_method, total, status, buyer_role, total_quantity,
               pricing_tier, discount_amount, razorpay_order_id,
               razorpay_payment_id, created_at
        FROM orders
        WHERE id = ?
        """,
        (order_id,),
    ).fetchone()

    if not row:
        connection.close()
        return None

    order = dict(row)
    item_rows = connection.execute(
        """
        SELECT product_name, variant_sku, variant_label, quantity,
               retail_unit_price, wholesale_unit_price,
               applied_unit_price, line_total
        FROM order_items
        WHERE order_id = ?
        ORDER BY id
        """,
        (order_id,),
    ).fetchall()
    connection.close()
    order["items"] = [dict(item_row) for item_row in item_rows]
    return order


def list_orders(limit: int = 100) -> list[dict[str, Any]]:
    connection = get_connection()
    rows = connection.execute(
        """
        SELECT id
        FROM orders
        ORDER BY created_at DESC, id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    connection.close()
    return [get_order(row[0]) for row in rows]


