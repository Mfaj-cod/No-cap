# NoCaps - E-Commerce Cap Store

[![Tests](https://img.shields.io/badge/tests-154%20passing-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)]()
[![FastAPI](https://img.shields.io/badge/fastapi-0.100%2B-green)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

A modern, production-ready e-commerce platform for selling premium caps. Built with **FastAPI**, featuring real-time cart management, Razorpay payments, AI-powered support, and a comprehensive admin dashboard.

---

## Quick Start

### 1. Clone & Setup
```bash
git clone <repository-url>
cd Nocap
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Initialize Database & Run
```bash
python -c "from src.db import init_database; init_database()"
uvicorn app:app --reload --port 8000
```

Visit: `http://localhost:8000`

---

## Features

### E-Commerce
- **Product Catalog**: Browse, search, and filter caps by category/price
- **Shopping Cart**: Session-based cart with real-time updates
- **Orders**: Guest & registered user checkout with order tracking
- **Inventory**: Stock management with variant support (color, size)
- **Reviews**: Customer ratings and feedback

### Payments
- **Razorpay Integration**: Online payment processing (UPI, Cards, Wallets)
- **Cash on Delivery**: Alternative payment method
- **Payment Verification**: Secure signature validation
- **Order Confirmation**: Automated email notifications

### User Management
- **Authentication**: Session-based login/register
- **Security**: PBKDF2-HMAC-SHA256 password hashing (200k iterations)
- **Roles**: Customer, Shop Owner (wholesale pricing), Admin
- **Account**: Dashboard with order history and profile management

### AI Support
- **CapAI**: LLM-powered customer service chatbot (Groq API)
- **Smart Responses**: Context-aware answers using product catalog
- **Fallback**: Safe escalation to human support

### Email & Notifications
- **Order Confirmations**: Beautiful HTML emails via SMTP
- **Password Reset**: OTP-based password recovery
- **Contact Forms**: Customer inquiries to admin
- **Newsletters**: Subscription management
- **Background Processing**: Non-blocking email with threading

### Admin Features
- **Orders Dashboard**: View, manage, and update order status
- **Customer Management**: User list and account overview
- **Analytics**: Order activity and engagement tracking

---

## Architecture

### Tech Stack
| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI |
| **Framework** | Starlette |
| **Database** | SQLite3 |
| **Frontend** | Jinja2 + HTML5/CSS3/JavaScript |
| **Auth** | Session middleware + PBKDF2 hashing |
| **Payments** | Razorpay API |
| **AI/LLM** | Groq API (llama-3.3-70b) |
| **Email** | SMTP (threading) |
| **Testing** | pytest + pytest-cov + httpx |
| **Deployment** | Docker + Render/Heroku |

### System Flow

```
User Request
    ↓
[Middleware: Sessions, CORS]
    ↓
[FastAPI Routes]
    ├─ GET /products        → Storefront
    ├─ POST /add_to_cart    → Cart Service
    ├─ GET /checkout       → Orders Module
    ├─ POST /success       → Payment Verification
    ├─ GET /account        → User Dashboard
    ├─ POST /contact       → Email (Background Thread)
    └─ POST /customer-care → AI Support
    ↓
[Database: SQLite]
    ├─ users
    ├─ products
    ├─ orders
    ├─ subscriptions
    └─ order_activity
    ↓
[Response: HTML/JSON]
```

---

## Project Structure

```
Nocap/
├── app.py                    # FastAPI entrypoint
├── requirements.txt          # Dependencies
├── .env.example             # Environment template
├── README.md                # (this file)
├── Dockerfile               # Container configuration
├── Procfile                 # Heroku deployment
│
├── src/                     # Application code
│   ├── app.py              # Setup, middleware, lifespan
│   ├── auth_routes.py      # Login, register, password reset (OTP)
│   ├── cart_routes.py      # Add/update/remove cart items
│   ├── orders_routes.py    # Checkout, payment verification, order status
│   ├── storefront_routes.py # Products, categories, search, filters
│   ├── admin_routes.py     # Admin orders dashboard, API
│   ├── engagement_routes.py # Contact forms, subscriptions
│   ├── support_routes.py    # AI support chat (CapAI)
│   ├── ai_support.py        # Groq LLM integration
│   ├── db.py               # Database: SQLite operations
│   ├── config.py           # Settings from .env
│   ├── services.py         # Business logic: cart, checkout, sessions
│   ├── security.py         # Password hashing (PBKDF2)
│   ├── notifications.py    # Email: background threading
│   └── web.py              # Jinja2 template rendering + context
│
├── static/
│   ├── css/style.css       # Dark theme with accent colors
│   ├── js/app.js           # Client-side interactivity
│   └── img/                # Product images by category
│
├── templates/              # Jinja2 HTML
│   ├── base.html          # Navigation, footer, layout
│   ├── index.html         # Homepage with featured products
│   ├── product.html       # Product detail with variants
│   ├── category.html      # Category listings
│   ├── cart.html          # Shopping cart & summary
│   ├── checkout.html      # Order form + payment
│   ├── account.html       # User account & orders
│   ├── login.html         # Login form
│   ├── register.html      # Registration form
│   ├── contact.html       # Contact form
│   ├── customer_care.html # AI support chat
│   ├── success.html       # Payment success
│   └── failure.html       # Payment failure
│
└── tests/                  # Automated test suite (154 tests)
    ├── conftest.py         # Shared fixtures, isolated test DB
    ├── test_health.py      # Health-check endpoint
    ├── test_security.py    # Password hashing unit tests
    ├── test_services.py    # Cart helpers, flash messages
    ├── test_db.py          # Database CRUD & OTP reset flow
    ├── test_auth.py        # Register, login, logout, account guard
    ├── test_storefront.py  # Product filters, search, HTTP routes
    ├── test_cart.py        # Add / update / remove cart items
    ├── test_orders.py      # Checkout (COD), success/failure pages
    ├── test_engagement.py  # Contact form, newsletter subscribe
    ├── test_admin.py       # Admin routes & 403 enforcement
    └── test_pricing.py     # Wholesale / retail pricing logic

```

---

## Database Schema

```sql
users (id, name, email, password_hash, role, reset_otp, reset_otp_expiry)
products (id, name, category, description, normal_price, shop_owner_price, featured, stock)
product_variants (id, product_id, sku, color, size, stock_quantity)
orders (id, user_id, status, payment_method, total, items_json, checkout_data_json, created_at)
order_activity (id, order_id, email, phone, address, timestamp) -- fraud detection
subscriptions (id, email, created_at)
categories (id, name, image_url)
```

---

## Development Workflow

### 1. Code Organization
- **Routes** (`src/*_routes.py`): HTTP endpoints, validation
- **Services** (`src/services.py`): Business logic, pure functions
- **Database** (`src/db.py`): CRUD operations
- **Config** (`src/config.py`): Environment settings

### 2. Adding a New Feature

**Example: New promotion endpoint**

```python
# src/promo_routes.py
from fastapi import APIRouter
from src.web import render_template

router = APIRouter()

@router.get("/promo/{code}", name="apply_promo")
def apply_promo(code: str):
    # Business logic in services.py
    discount = validate_promo_code(code)
    return {"discount": discount}
```

Then in `app.py`:
```python
from src.promo_routes import router as promo_router
app.include_router(promo_router)
```

### 3. Template Context
All templates receive via `render_template()`:
```python
{
    "request": request,           # FastAPI request object
    "current_user": {...},        # Logged-in user or None
    "cart_count": 5,              # Items in cart
    "store_name": "NoCaps",       # Brand name
    "current_year": 2026,         # For footer
    "flash_messages": [
        {"category": "success", "message": "Order placed!"}
    ],
    # + any custom context from route
}
```

### 4. Debugging

**Enable detailed logging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
```

**Test database state**:
```bash
# SQLite CLI
sqlite3 store.db
sqlite> SELECT * FROM users;
```

**Inspect requests/responses**:
```python
# In uvicorn terminal, you'll see all requests logged
# Or use Python debugger:
import pdb; pdb.set_trace()
```
---

## Dependencies

```
fastapi==0.100+          # Web framework
uvicorn==0.23+           # ASGI server
starlette==0.27+         # Async toolkit
jinja2==3.1+             # Templates
python-multipart==0.0+   # Form parsing
razorpay==1.3+           # Payment gateway
groq==0.4+               # LLM API
python-dotenv==1.0+      # Environment variables

# Testing
pytest==7.4+
pytest-cov==4.0+
httpx==0.24+
```

---

## Environment Variables Reference

Create `.env` file in project root:

```bash
# ===== REQUIRED =====
SESSION_SECRET=your-secret-key-here-change-in-production

# ===== OPTIONAL: Email Configuration =====
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-specific-password
OWNER_EMAIL=owner@example.com

# ===== OPTIONAL: Payments =====
RAZORPAY_KEY_ID=your_key_id
RAZORPAY_KEY_SECRET=your_key_secret

# ===== OPTIONAL: AI Support =====
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama-3.3-70b-versatile

# ===== OPTIONAL: Database =====
DATABASE_PATH=./nocap.db
```

**Getting Credentials:**
- **Gmail App Password**: https://myaccount.google.com/apppasswords (require 2FA enabled)
- **Razorpay**: https://razorpay.com/dashboard
- **Groq API Key**: https://console.groq.com

---

## Security

### Password Security
- **Algorithm**: PBKDF2-HMAC-SHA256 with 200,000 iterations
- **Hashing**: In [src/security.py](src/security.py#L10)
- **Verification**: Timing-attack resistant comparison

### Session Security
- **Storage**: Server-side with Starlette SessionMiddleware
- **Encryption**: Signed with `SESSION_SECRET`
- **HttpOnly**: Session cookies not accessible to JavaScript
- **SameSite**: Strict CSRF protection

### Payment Security
- **Verification**: Razorpay signature validation on server
- **Keys**: Never exposed in frontend
- **Webhook**: Signed callback verification

---

## Monitoring & Logging

### Log Output
All important operations logged to stdout:
```
[2024-01-15 10:30:45] Order #123 placed - user: john@example.com
[2024-01-15 10:30:46] Order email sent (background) - order: 123
[2024-01-15 10:30:47] Payment verified - razorpay_id: pay_12345
```

### Debugging Email
Check `src/notifications.py`:
```python
# Email runs in background - check logs for delivery status
# Won't block order completion if SMTP fails
# Includes retry logic with timeout
```

### Database Queries
Enable SQL logging in [src/db.py](src/db.py#L1):
```python
import logging
logging.getLogger("sqlite3").setLevel(logging.DEBUG)
```

---

## Deployment Guide

### Local Development
```bash
uvicorn app:app --reload --port 8000
```

### Docker
```bash
# Build
docker build -t nocap .

# Run
docker run -p 8000:8000 --env-file .env nocap
```

### Render.com (Recommended)
```bash
# Create render.yaml (included)
# Connect GitHub repo
# Auto-deploys on push
# Environment variables in Render dashboard
```

```

**Important**: SMTP port 587 blocked on free Render tier. Use:
- SendGrid (free tier available)
- Mailgun (free for testing)
- AWS SES
- Or use our built-in background threading (included)
```
---

## Code Examples

### Email Template Customization
```python
# src/notifications.py - modify html_content variable
# Uses HTML for beautiful formatting
# Logged if send fails
```

### AI Support Customization
```python
# src/ai_support.py - modify system prompt
# Uses Groq llama-3.3-70b-versatile model
# Falls back to escalation if API fails
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| `TemplateNotFound` | Check template name in route matches file in `templates/` |
| Session lost | Check SessionMiddleware in app.py, ensure cookie domain correct |
| SMTP timeout | Normal on Render - emails sent in background with 10s timeout |
| 404 on CSS/JS | Check static files served by `StaticFiles` in app.py |
| Cart empties on refresh | Normal - session expires, clear session in browser settings |
| Razorpay fails | Check keys, wait 2 mins between test transactions |

---

## Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Starlette Docs**: https://www.starlette.io/
- **Jinja2 Docs**: https://jinja.palletsprojects.com/
- **SQLite Docs**: https://www.sqlite.org/docs.html
- **Razorpay API**: https://razorpay.com/docs/
- **Groq API**: https://console.groq.com/docs/

---

## Contributing

### Setup Development Environment
```bash
git clone <repo>
cd Nocap
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Making Changes
1. Create feature branch: `git checkout -b feature/name`
2. Commit: `git commit -am "Add feature"`
3. Push and create PR

### Code Style
- Follow PEP 8
- Use type hints where applicable
- Add docstrings for public functions
- Write tests for new features

---

## Testing

The project ships with a full automated test suite covering every feature area. Tests use an isolated in-project SQLite database so the production `store.db` is never touched.

### Run Locally

```bash
# Install dependencies (includes pytest, pytest-cov, httpx)
pip install -r requirements.txt

# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=src --cov-report=term-missing

# Run only a specific feature area
pytest tests/ -m auth        # auth tests
pytest tests/ -m cart        # cart tests
pytest tests/ -m unit        # unit tests only (no HTTP)
pytest tests/ -m integration # integration / HTTP tests
```

### Test Coverage

| File | What is tested |
|---|---|
| `test_health.py` | `/health` endpoint |
| `test_security.py` | PBKDF2 hashing, salt uniqueness, verify correct/wrong/malformed |
| `test_services.py` | Cart key helpers, flash messages, session cart save/get/clear |
| `test_db.py` | Product queries, variant helpers, user CRUD, OTP reset, subscriptions |
| `test_auth.py` | Register validation, login/logout, account auth guard, forgot-password flow |
| `test_storefront.py` | Product filters, search relevance scoring, index/product/category routes |
| `test_cart.py` | Add, update (zero→remove), remove; stock-capping, unknown product |
| `test_orders.py` | COD checkout, cart cleared after order, success/failure page access control |
| `test_engagement.py` | Contact form (with/without SMTP), newsletter subscription |
| `test_admin.py` | 403 for non-admin, orders page, JSON API shape, status update |
| `test_pricing.py` | Wholesale threshold, 25% discount math, retail fallback, guest pricing |

### CI Pipeline

Tests run automatically on every push and pull request to `main` via GitHub Actions:

```
push / PR to main
    ↓
[Install Python 3.12 + dependencies]
    ↓
[pytest tests/ --cov=src]  ← must pass before deploy
    ↓
[Upload coverage.xml artifact]
    ↓
[Trigger Render deploy hook]  ← only on main branch push
```

---

## Project Status

| Component | Status |
|-----------|--------|
| Core E-Commerce | ✅ Production Ready |
| User Auth | ✅ Secure (PBKDF2) |
| Payments | ✅ Razorpay Integrated |
| Email | ✅ Background Threading |
| AI Support | ✅ Groq Integration |
| Admin Dashboard | ✅ Order Management |
| Mobile Responsive | ✅ Bootstrap Compatible |
| Testing | ✅ 154 Tests — All Passing |
| CI/CD | ✅ GitHub Actions (push + PR) |

---

## Support & Contact

- **Issues**: Create GitHub issue with detailed reproduction steps
- **Feature Requests**: Submit as GitHub discussion
- **Email**: Use contact form in application
- **AI Support**: Try CapAI chatbot in customer care section

---

## License

MIT License - See LICENSE file for details

---

**Last Updated**: April 2026
**Maintainer**: https://github.com/Mfaj-cod
**Version**: 1.0.1
