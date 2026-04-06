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
        "description": "Lightweight performance cap with moisture control for training days, clubs, and team orders.",
        "normal_price": 49.0,
        "image_url": "/static/img/sports/sport-1.jpeg",
        "category": "Sports",
        "details": ["Breathable mesh panels", "Sweat-wicking band", "Adjustable rear strap"],
        "attributes": {
            "Material": "Performance polyester",
            "Fit": "Adjustable one size",
            "Brim": "Curved athletic brim",
            "Best For": "Training, team kits, academy merch",
        },
        "variants": [
            {"sku": "VEL-BLK-OS", "color": "Black", "size": "One Size", "stock_quantity": 48},
            {"sku": "VEL-NVY-OS", "color": "Navy", "size": "One Size", "stock_quantity": 35},
            {"sku": "VEL-RED-OS", "color": "Red", "size": "One Size", "stock_quantity": 22},
        ],
        "reviews": [
            {"user": "Rohit", "date": "2026-04-01", "rating": 5, "comment": "Comfortable for long practice sessions."}
        ],
        "featured": True,
    },
    {
        "id": 2,
        "name": "Weekend Casual Cap",
        "description": "Classic everyday cap with a soft curved brim and easy all-day fit.",
        "normal_price": 649.0,
        "image_url": "/static/img/casual/casual-2.jpeg",
        "media_gallery": [
            "/static/img/placeholder.jpg",
            "/static/img/bg2.jpg",
            "/static/img/logo.jpg",
        ],
        "category": "Casual",
        "details": ["Washed cotton finish", "Curved visor", "Everyday streetwear styling"],
        "attributes": {
            "Material": "Washed cotton twill",
            "Fit": "Relaxed one size",
            "Closure": "Metal buckle strap",
            "Best For": "Daily wear, gifting, lifestyle retail",
        },
        "variants": [
            {"sku": "WKC-TAN-OS", "color": "Tan", "size": "One Size", "stock_quantity": 30},
            {"sku": "WKC-OLV-OS", "color": "Olive", "size": "One Size", "stock_quantity": 24},
            {"sku": "WKC-BLK-OS", "color": "Black", "size": "One Size", "stock_quantity": 41},
        ],
        "reviews": [
            {"user": "Priya", "date": "2026-03-30", "rating": 4, "comment": "Easy to pair with almost any outfit."}
        ],
        "featured": True,
    },
    {
        "id": 3,
        "name": "Street Snapback Pro",
        "description": "Structured snapback built for bold branding, events, and premium retail shelves.",
        "normal_price": 899.0,
        "image_url": "/static/img/snapback/snapback-1.jpeg",
        "media_gallery": [
            "/static/img/placeholder.jpg",
            "/static/img/logo.jpg",
            "/static/img/bg1.jpg",
        ],
        "category": "Snapback",
        "details": ["Flat brim", "Structured front", "Ideal for logo embroidery"],
        "attributes": {
            "Material": "Structured acrylic blend",
            "Fit": "Snapback adjustable",
            "Panel Style": "6-panel crown",
            "Best For": "Events, brand merch, storefront resale",
        },
        "variants": [
            {"sku": "SSP-BLK-OS", "color": "Black", "size": "One Size", "stock_quantity": 18},
            {"sku": "SSP-WHT-OS", "color": "White", "size": "One Size", "stock_quantity": 16},
            {"sku": "SSP-GRY-OS", "color": "Grey", "size": "One Size", "stock_quantity": 12},
        ],
        "reviews": [],
        "featured": True,
    },
    {
        "id": 4,
        "name": "Breeze Trucker Cap",
        "description": "Airy trucker-style cap with mesh back panels and a durable front face.",
        "normal_price": 699.0,
        "image_url": "/static/img/placeholder.jpg",
        "media_gallery": [
            "/static/img/placeholder.jpg",
            "/static/img/bg2.jpg",
            "/static/img/logo.jpg",
        ],
        "category": "Trucker",
        "details": ["Mesh back", "Foam front panel", "Lightweight road-trip fit"],
        "attributes": {
            "Material": "Foam front with mesh back",
            "Fit": "Snap closure one size",
            "Brim": "Curved trucker brim",
            "Best For": "Summer retail, travel, promo runs",
        },
        "variants": [
            {"sku": "BTC-BLK-OS", "color": "Black", "size": "One Size", "stock_quantity": 26},
            {"sku": "BTC-BLU-OS", "color": "Blue", "size": "One Size", "stock_quantity": 20},
            {"sku": "BTC-CRM-OS", "color": "Cream", "size": "One Size", "stock_quantity": 14},
        ],
        "reviews": [],
        "featured": False,
    },
    {
        "id": 5,
        "name": "Heritage Dad Cap",
        "description": "Relaxed dad cap with a broken-in feel and subtle premium stitching.",
        "normal_price": 749.0,
        "image_url": "/static/img/Dad-Cap/dadcap-1.jpeg",
        "media_gallery": [
            "/static/img/placeholder.jpg",
            "/static/img/bg1.jpg",
            "/static/img/logo.jpg",
        ],
        "category": "Dad Cap",
        "details": ["Unstructured crown", "Soft cotton twill", "Vintage-inspired fit"],
        "attributes": {
            "Material": "Soft cotton twill",
            "Fit": "Relaxed adjustable",
            "Closure": "Antique buckle strap",
            "Best For": "Everyday casual, cafe merch, gifting",
        },
        "variants": [
            {"sku": "HDC-NVY-OS", "color": "Navy", "size": "One Size", "stock_quantity": 28},
            {"sku": "HDC-BRG-OS", "color": "Burgundy", "size": "One Size", "stock_quantity": 17},
            {"sku": "HDC-SND-OS", "color": "Sand", "size": "One Size", "stock_quantity": 19},
        ],
        "reviews": [
            {"user": "Aman", "date": "2026-03-28", "rating": 5, "comment": "The fit feels instantly familiar."}
        ],
        "featured": True,
    },
    {
        "id": 6,
        "name": "Urban Knit Beanie",
        "description": "Cold-weather beanie with stretch knit comfort for casual and retail bundles.",
        "normal_price": 599.0,
        "image_url": "/static/img/placeholder.jpg",
        "media_gallery": [
            "/static/img/placeholder.jpg",
            "/static/img/bg2.jpg",
            "/static/img/logo.jpg",
        ],
        "category": "Beanie",
        "details": ["Soft rib knit", "Fold-over cuff", "Unisex styling"],
        "attributes": {
            "Material": "Acrylic knit",
            "Fit": "Stretch free size",
            "Warmth": "Light-to-medium winter layer",
            "Best For": "Winter retail, layering, campus merch",
        },
        "variants": [
            {"sku": "UKB-BLK-FS", "color": "Black", "size": "Free Size", "stock_quantity": 40},
            {"sku": "UKB-MST-FS", "color": "Mustard", "size": "Free Size", "stock_quantity": 18},
            {"sku": "UKB-CHR-FS", "color": "Charcoal", "size": "Free Size", "stock_quantity": 21},
        ],
        "reviews": [],
        "featured": False,
    },
    {
        "id": 7,
        "name": "Clubhouse Sports Visor Cap",
        "description": "Low-profile sports cap with a sleek look for clubs, academies, and event uniforms.",
        "normal_price": 829.0,
        "image_url": "/static/img/placeholder.jpg",
        "media_gallery": [
            "/static/img/placeholder.jpg",
            "/static/img/bg1.jpg",
            "/static/img/logo.jpg",
        ],
        "category": "Sports",
        "details": ["Quick-dry fabric", "Slim profile", "Event-ready finish"],
        "attributes": {
            "Material": "Quick-dry synthetic blend",
            "Fit": "Adjustable one size",
            "Profile": "Low-profile sporty crown",
            "Best For": "Clubs, tournaments, event uniforms",
        },
        "variants": [
            {"sku": "CSV-WHT-OS", "color": "White", "size": "One Size", "stock_quantity": 23},
            {"sku": "CSV-NVY-OS", "color": "Navy", "size": "One Size", "stock_quantity": 20},
            {"sku": "CSV-RED-OS", "color": "Red", "size": "One Size", "stock_quantity": 15},
        ],
        "reviews": [],
        "featured": False,
    },
    {
        "id": 8,
        "name": "Canvas Casual Camp Cap",
        "description": "Five-panel camp cap with sturdy canvas texture for modern casual drops.",
        "normal_price": 779.0,
        "image_url": "/static/img/placeholder.jpg",
        "media_gallery": [
            "/static/img/placeholder.jpg",
            "/static/img/bg2.jpg",
            "/static/img/logo.jpg",
        ],
        "category": "Casual",
        "details": ["Five-panel design", "Canvas body", "Clean front for branding"],
        "attributes": {
            "Material": "Structured canvas",
            "Fit": "Webbing strap adjuster",
            "Panel Style": "5-panel camp cap",
            "Best For": "Streetwear, custom branding, drops",
        },
        "variants": [
            {"sku": "CCC-OLV-OS", "color": "Olive", "size": "One Size", "stock_quantity": 25},
            {"sku": "CCC-BEI-OS", "color": "Beige", "size": "One Size", "stock_quantity": 18},
            {"sku": "CCC-BLK-OS", "color": "Black", "size": "One Size", "stock_quantity": 29},
        ],
        "reviews": [],
        "featured": False,
    },
]

# Dynamically append a product entry for each cap image found under static/img
# This keeps `PRODUCTS` in sync with the repository images without hardcoding hundreds
from pathlib import Path

def _generate_products_from_images():
    project_root = Path(__file__).resolve().parent.parent
    img_dir = project_root / "static" / "img"
    if not img_dir.exists():
        return

    existing_urls = {p.get("image_url") for p in PRODUCTS if p.get("image_url")}
    next_id = max((p.get("id", 0) for p in PRODUCTS), default=0) + 1
    suffixes = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

    for folder in sorted(img_dir.iterdir()):
        if not folder.is_dir():
            continue
        category = folder.name.replace("-", " ").replace("_", " ").title()
        for img in sorted(folder.iterdir()):
            if img.suffix.lower() not in suffixes:
                continue
            # skip generic assets
            if any(tok in img.name.lower() for tok in ("logo", "placeholder", "bg")):
                continue
            rel = img.relative_to(project_root).as_posix()  # e.g. static/img/sports/sport-1.jpeg
            image_url = "/" + rel
            if image_url in existing_urls:
                continue

            # build a friendly name from folder and filename
            stem_parts = img.stem.split('-')
            idx = stem_parts[-1] if stem_parts[-1].isdigit() else None
            if idx:
                name = f"{category} Cap {idx}"
            else:
                name = f"{category} Cap {img.stem}"

            product = {
                "id": next_id,
                "name": name,
                "description": f"Designed from the {category.lower()} collection image.",
                "normal_price": 799.0,
                "image_url": image_url,
                "media_gallery": [image_url],
                "category": category,
                "details": ["Quality fit", "Adjustable closure", "Durable brim"],
                "attributes": {"Material": "Cotton blend", "Fit": "One Size", "Best For": "Everyday wear"},
                "variants": [
                    {"sku": f"{img.stem.upper().replace('-','')}-BLK-OS", "color": "Black", "size": "One Size", "stock_quantity": 20},
                    {"sku": f"{img.stem.upper().replace('-','')}-WHT-OS", "color": "White", "size": "One Size", "stock_quantity": 15},
                    {"sku": f"{img.stem.upper().replace('-','')}-NVY-OS", "color": "Navy", "size": "One Size", "stock_quantity": 12},
                ],
                "reviews": [],
                "featured": False,
            }

            PRODUCTS.append(product)
            existing_urls.add(image_url)
            next_id += 1


_generate_products_from_images()

SUPPORT_POLICIES = """
Store focus: caps for normal customers and bulk-buying shop owners.
Bulk pricing: shop owners get 25% off the full cart once the cart quantity reaches at least 25 items.
Retail fallback: shop owners with fewer than 25 items can still checkout, but they pay retail pricing.
Shipping: orders are usually dispatched in 1-2 business days and delivered within 3-7 business days across India.
Returns: unworn items with a manufacturing issue can be reported within 7 days of delivery.
Escalation: for account-specific or order-specific help, direct customers to the contact page or their account page instead of inventing private order details.
Tone: helpful, concise, and sales-supportive.
"""
