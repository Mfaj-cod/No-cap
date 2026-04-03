WHOLESALE_THRESHOLD = 25
WHOLESALE_DISCOUNT = 0.25

CATEGORIES = [
    {"name": "Sports", "image_url": "/static/img/logo.jpg"},
    {"name": "Casual", "image_url": "/static/img/placeholder.jpg"},
    {"name": "Snapback", "image_url": "/static/img/placeholder.jpg"},
    {"name": "Trucker", "image_url": "/static/img/placeholder.jpg"},
    {"name": "Dad Cap", "image_url": "/static/img/placeholder.jpg"},
    {"name": "Beanie", "image_url": "/static/img/logo.jpg"},
]

PRODUCTS = [
    {
        "id": 1,
        "name": "Velocity Sports Cap",
        "description": "Lightweight performance cap with moisture control for training days and team orders.",
        "normal_price": 799.0,
        "image_url": "/static/img/placeholder.jpg",
        "category": "Sports",
        "details": ["Breathable mesh panels", "Sweat-wicking band", "Adjustable rear strap"],
        "reviews": [
            {"user": "Rohit", "date": "2026-04-01", "comment": "Comfortable for long practice sessions."}
        ],
        "featured": True,
    },
    {
        "id": 2,
        "name": "Weekend Casual Cap",
        "description": "Classic everyday cap with a soft curved brim and easy all-day fit.",
        "normal_price": 649.0,
        "image_url": "/static/img/placeholder.jpg",
        "category": "Casual",
        "details": ["Washed cotton finish", "Curved visor", "Everyday streetwear styling"],
        "reviews": [
            {"user": "Priya", "date": "2026-03-30", "comment": "Easy to pair with almost any outfit."}
        ],
        "featured": True,
    },
    {
        "id": 3,
        "name": "Street Snapback Pro",
        "description": "Structured snapback built for bold branding, events, and premium retail shelves.",
        "normal_price": 899.0,
        "image_url": "/static/img/placeholder.jpg",
        "category": "Snapback",
        "details": ["Flat brim", "Structured front", "Ideal for logo embroidery"],
        "reviews": [],
        "featured": True,
    },
    {
        "id": 4,
        "name": "Breeze Trucker Cap",
        "description": "Airy trucker-style cap with mesh back panels and a durable front face.",
        "normal_price": 699.0,
        "image_url": "/static/img/placeholder.jpg",
        "category": "Trucker",
        "details": ["Mesh back", "Foam front panel", "Lightweight road-trip fit"],
        "reviews": [],
        "featured": False,
    },
    {
        "id": 5,
        "name": "Heritage Dad Cap",
        "description": "Relaxed dad cap with a broken-in feel and subtle premium stitching.",
        "normal_price": 749.0,
        "image_url": "/static/img/placeholder.jpg",
        "category": "Dad Cap",
        "details": ["Unstructured crown", "Soft cotton twill", "Vintage-inspired fit"],
        "reviews": [
            {"user": "Aman", "date": "2026-03-28", "comment": "The fit feels instantly familiar."}
        ],
        "featured": True,
    },
    {
        "id": 6,
        "name": "Urban Knit Beanie",
        "description": "Cold-weather beanie with stretch knit comfort for casual and retail bundles.",
        "normal_price": 599.0,
        "image_url": "/static/img/placeholder.jpg",
        "category": "Beanie",
        "details": ["Soft rib knit", "Fold-over cuff", "Unisex styling"],
        "reviews": [],
        "featured": False,
    },
    {
        "id": 7,
        "name": "Clubhouse Sports Visor Cap",
        "description": "Low-profile sports cap with a sleek look for clubs, academies, and event uniforms.",
        "normal_price": 829.0,
        "image_url": "/static/img/placeholder.jpg",
        "category": "Sports",
        "details": ["Quick-dry fabric", "Slim profile", "Event-ready finish"],
        "reviews": [],
        "featured": False,
    },
    {
        "id": 8,
        "name": "Canvas Casual Camp Cap",
        "description": "Five-panel camp cap with sturdy canvas texture for modern casual drops.",
        "normal_price": 779.0,
        "image_url": "/static/img/placeholder.jpg",
        "category": "Casual",
        "details": ["Five-panel design", "Canvas body", "Clean front for branding"],
        "reviews": [],
        "featured": False,
    },
]

SUPPORT_POLICIES = """
Store focus: caps for normal customers and bulk-buying shop owners.
Bulk pricing: shop owners get 25% off the full cart once the cart quantity reaches at least 25 items.
Retail fallback: shop owners with fewer than 25 items can still checkout, but they pay retail pricing.
Shipping: orders are usually dispatched in 3-5 business days and delivered within 3-7 business days across India.
Returns: unworn items with a manufacturing issue can be reported within 7 days of delivery.
Escalation: for account-specific or order-specific help, direct customers to the contact page or their account page instead of inventing private order details.
Tone: helpful, concise, and sales-supportive.
"""
