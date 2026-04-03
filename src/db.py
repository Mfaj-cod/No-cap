import json
import sqlite3
from typing import Any

from src.config import settings
from src.data import CATEGORIES, PRODUCTS, WHOLESALE_DISCOUNT

DB_SCHEMA_VERSION = 2


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
        DROP TABLE IF EXISTS order_items;
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS users;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS categories;
        DROP TABLE IF EXISTS subscriptions;

        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('customer', 'shop_owner')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            image_url TEXT NOT NULL
        );

        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            normal_price REAL NOT NULL,
            image_url TEXT NOT NULL,
            category TEXT NOT NULL,
            details TEXT NOT NULL,
            reviews TEXT NOT NULL,
            featured INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE orders (
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

        CREATE TABLE order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            retail_unit_price REAL NOT NULL,
            wholesale_unit_price REAL NOT NULL,
            applied_unit_price REAL NOT NULL,
            line_total REAL NOT NULL,
            FOREIGN KEY(order_id) REFERENCES orders(id)
        );

        CREATE TABLE subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )


def _seed_reference_data(connection: sqlite3.Connection) -> None:
    category_count = connection.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    product_count = connection.execute("SELECT COUNT(*) FROM products").fetchone()[0]

    if category_count == 0:
        connection.executemany(
            "INSERT INTO categories (name, image_url) VALUES (?, ?)",
            [(category["name"], category["image_url"]) for category in CATEGORIES],
        )

    if product_count == 0:
        connection.executemany(
            """
            INSERT INTO products
                (id, name, description, normal_price, image_url, category, details, reviews, featured)
            VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    product["id"],
                    product["name"],
                    product["description"],
                    product["normal_price"],
                    product["image_url"],
                    product["category"],
                    json.dumps(product["details"]),
                    json.dumps(product["reviews"]),
                    1 if product.get("featured") else 0,
                )
                for product in PRODUCTS
            ],
        )


def _product_from_row(row: sqlite3.Row) -> dict[str, Any]:
    normal_price = float(row["normal_price"])
    shop_owner_price = round(normal_price * (1 - WHOLESALE_DISCOUNT), 2)
    return {
        "id": row["id"],
        "name": row["name"],
        "description": row["description"],
        "normal_price": normal_price,
        "shop_owner_price": shop_owner_price,
        "image_url": row["image_url"],
        "category": row["category"],
        "details": json.loads(row["details"]) if row["details"] else [],
        "reviews": json.loads(row["reviews"]) if row["reviews"] else [],
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
        SELECT id, name, description, normal_price, image_url, category, details, reviews, featured
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
        SELECT id, name, description, normal_price, image_url, category, details, reviews, featured
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
    cursor.executemany(
        """
        INSERT INTO order_items
            (
                order_id, product_id, product_name, quantity,
                retail_unit_price, wholesale_unit_price, applied_unit_price, line_total
            )
        VALUES
            (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                order_id,
                item["product"]["id"],
                item["product"]["name"],
                item["quantity"],
                item["retail_unit_price"],
                item["wholesale_unit_price"],
                item["applied_unit_price"],
                item["line_total"],
            )
            for item in cart_summary["items"]
        ],
    )

    connection.commit()
    connection.close()
    return order_id


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
        SELECT product_name, quantity, retail_unit_price, wholesale_unit_price,
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

