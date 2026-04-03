import sqlite3
import json

DB_NAME = 'store.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        name TEXT
    )''')

    # Products table
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT,
        price REAL,
        image_url TEXT,
        category TEXT,
        ingredients TEXT,   -- JSON list
        reviews TEXT        -- JSON list of {user, date, comment}
    )''')

    # Categories table
    c.execute('''CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        image_url TEXT
    )''')

    # Add category column to products
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        title TEXT,
        description TEXT,
        price REAL,
        image TEXT,
        category TEXT
    )''')


    # Orders table
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        email TEXT,
        phone TEXT,
        address TEXT,
        city TEXT,
        state TEXT,
        pincode TEXT,
        payment_method TEXT,
        total REAL,
        status TEXT DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Order items table
    c.execute('''CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        price REAL
    )''')

    # Subscriptions table
    c.execute('''CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    conn.commit()
    conn.close()


def insert_products(products):
    """
    products: list of dicts with keys:
    id, name, description, price, image_url, category, ingredients (list), reviews (list of dicts)
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    for p in products:
        ingredients_json = json.dumps(p.get('ingredients', []))
        reviews_json = json.dumps(p.get('reviews', []))
        c.execute('''INSERT OR REPLACE INTO products 
                     (id, name, description, price, image_url, category, ingredients, reviews) 
                     VALUES (?,?,?,?,?,?,?,?)''',
                  (p['id'], p['name'], p['description'], p['price'], p['image_url'], p.get('category',''), ingredients_json, reviews_json))
    conn.commit()
    conn.close()


def insert_categories(categories):
    """
    categories: list of dicts with keys: name, image_url
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    for cat in categories:
        c.execute('''INSERT OR REPLACE INTO categories (name, image_url) VALUES (?,?)''',
                  (cat['name'], cat['image_url']))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    # Example insert
    sample_products = [
        {
            "id": 1,
            "name": "Black Pepper",
            "description": "Freshly harvested black pepper from Kerala.",
            "price": 250,
            "image_url": "/static/images/black_pepper.jpg",
            "category": "Whole Spices",
            "ingredients": ["Black Pepper"],
            "reviews": [{"user": "Alice", "date": "2025-09-28", "comment": "Excellent quality!"}]
        },

        {
            "id": 2,
            "name": "Turmeric Powder",
            "description": "Organic turmeric powder with vibrant color.",
            "price": 180,
            "image_url": "/static/images/turmeric.jpg",
            "category": "Ground Spices",
            "ingredients": ["Turmeric"],
            "reviews": [{"user": "Alice", "date": "2025-09-28", "comment": "Excellent quality!"}]
        }
    ]

    sample_categories = [
        {"name": "Whole Spices", "image_url": "/static/images/whole_spices.jpg"},
        {"name": "Ground Spices", "image_url": "/static/images/ground_spices.jpg"},
        {"name": "Spice Blends", "image_url": "/static/images/spice_blends.jpg"},
        {"name": "Gift Sets", "image_url": "/static/images/gift_sets.jpg"}
    ]

    insert_products(sample_products)
    insert_categories(sample_categories)
