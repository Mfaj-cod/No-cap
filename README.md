# NoCaps - E-Commerce Cap Store

A modern, feature-rich e-commerce platform built with FastAPI for selling premium caps. The application includes user authentication, shopping cart management, order processing, and AI-powered customer support.

## Features

### Core E-Commerce
- Product browsing with advanced filtering (category, price, featured items)
- Real-time product search functionality
- Session-based shopping cart management
- Secure checkout with multiple payment options
- Order management and order history
- Product reviews and ratings

### User Management
- Customer registration and authentication
- Secure password hashing (PBKDF2-HMAC-SHA256)
- Shop owner roles with admin capabilities
- User account dashboard
- Email-based authentication

### Customer Engagement
- Newsletter subscription management
- Contact form with email notifications
- AI-powered support chatbot (powered by Groq LLM)
- Customer support integration

### Payment Processing
- Razorpay payment gateway integration
- Multiple payment method support
- Payment verification and order confirmation

### Admin Features
- Shop owner dashboard
- Order and sales management
- Customer management
- Subscription list management

## Tech Stack

- **Backend**: FastAPI + Starlette
- **Database**: SQLite3
- **Authentication**: Custom JWT/session-based with password hashing
- **Frontend**: Jinja2 templates with HTML/CSS/JavaScript
- **Email**: SMTP for notifications
- **AI/LLM**: LangChain + Groq API
- **Testing**: pytest with comprehensive test suite
- **Deployment**: Docker, Procfile (Heroku-ready)

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Git (for version control)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Nocap
```

### 2. Create a Virtual Environment
```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create --name nocap python=3.8
conda activate nocap
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root with the following variables:

```env
# Session Management (Required)
SESSION_SECRET=your-secret-key-change-in-production

# Payment Gateway (Optional - Razorpay)
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_secret_key

# Email Configuration (Optional - for contact forms)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
OWNER_EMAIL=owner@example.com

# AI Support (Optional - Groq LLM)
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama-3.1-8b-instant

# Database (Optional - defaults to ./nocap.db)
DATABASE_PATH=./nocap.db
```

**Note**: 
- `SESSION_SECRET` is the only truly required variable
- Optional variables will have sensible defaults or graceful fallbacks
- For Razorpay: Get keys from your Razorpay dashboard
- For Email: Use an app-specific password (not your regular Gmail password)
- For Groq: Sign up at https://console.groq.com/ for free API access

### 5. Initialize the Database
```bash
python -c "from src.db import init_database; init_database()"
```

This will:
- Create the SQLite database
- Set up all required tables (users, products, categories, orders, subscriptions, etc.)
- Seed the database with product catalog

## Running the Application

### Development Server
```bash
# Using uvicorn directly
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Or using Python module
python -m uvicorn app:app --reload
```

The application will be available at `http://localhost:8000`

### Production Deployment

#### Docker
```bash
# Build the Docker image
docker build -t nocap .

# Run the container
docker run -p 8000:8000 --env-file .env nocap
```

#### Heroku
The project includes a `Procfile` configured for Heroku deployment:
```bash
heroku create your-app-name
git push heroku main
```

## Testing

The project includes a comprehensive test suite with 183 tests covering all functionality.

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Specific Test File
```bash
python -m pytest tests/test_auth_routes.py -v
```

### Generate Coverage Report
```bash
python -m pytest tests/ --cov=src --cov-report=html
```

### Test Files
- `test_app.py` - Application initialization and route setup
- `test_auth_routes.py` - User authentication (login, register, logout)
- `test_cart_routes.py` - Shopping cart operations
- `test_config.py` - Configuration and environment variable loading
- `test_db.py` - Database operations and data models
- `test_engagement_routes.py` - Contact forms and subscriptions
- `test_orders_routes.py` - Checkout and order processing
- `test_security.py` - Password hashing and security
- `test_services.py` - Business logic (cart, checkout, sessions)
- `test_storefront_routes.py` - Product browsing and search

**Test Status**: ✅ 183 tests passing (100%)

## Project Structure

```
Nocap/
├── app.py                          # Main FastAPI application
├── Dockerfile                      # Docker configuration
├── Procfile                        # Heroku deployment configuration
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── nocap.db                        # SQLite database (auto-created)
│
├── src/                            # Source code directory
│   ├── __init__.py
│   ├── ai_support.py              # AI chatbot support integration
│   ├── auth_routes.py             # Authentication routes (login/register)
│   ├── cart_routes.py             # Shopping cart routes
│   ├── config.py                  # Configuration and settings
│   ├── data.py                    # Product catalog and constants
│   ├── db.py                      # Database operations
│   ├── engagement_routes.py       # Contact form and subscriptions
│   ├── init_db.py                 # Database initialization
│   ├── orders_routes.py           # Checkout and orders
│   ├── security.py                # Password hashing utilities
│   ├── services.py                # Business logic (cart, session, checkout)
│   ├── storefront_routes.py       # Product browsing routes
│   ├── support_routes.py          # Customer support routes
│   └── web.py                     # Template rendering utilities
│
├── static/                         # Static files
│   ├── css/
│   │   └── style.css              # Application styling
│   ├── js/
│   │   └── app.js                 # Frontend JavaScript
│   └── img/                       # Product images
│       ├── beanie/
│       ├── casual/
│       ├── Dadcap/
│       ├── snapback/
│       ├── sports/
│       └── trucker/
│
├── templates/                      # Jinja2 HTML templates
│   ├── base.html                  # Base template
│   ├── index.html                 # Home page
│   ├── product.html               # Product detail page
│   ├── category.html              # Category listing
│   ├── cart.html                  # Shopping cart
│   ├── checkout.html              # Checkout form
│   ├── login.html                 # Login form
│   ├── register.html              # Registration form
│   ├── account.html               # User account dashboard
│   ├── contact.html               # Contact form
│   ├── customer_care.html         # Customer support
│   ├── about.html                 # About page
│   └── success.html / failure.html # Payment result pages
│
└── tests/                          # Test suite
    ├── conftest.py                # Pytest fixtures and configuration
    ├── pytest.ini                 # Pytest configuration
    ├── test_app.py
    ├── test_auth_routes.py
    ├── test_cart_routes.py
    ├── test_config.py
    ├── test_db.py
    ├── test_engagement_routes.py
    ├── test_orders_routes.py
    ├── test_security.py
    ├── test_services.py
    ├── test_storefront_routes.py
    └── README.md                  # Testing documentation
```

## Database Schema

### Core Tables
- **users** - User accounts with role-based access (customer/shop_owner)
- **categories** - Product categories (Beanie, Casual, Dadcap, etc.)
- **products** - Product catalog with pricing and descriptions
- **product_variants** - Product variants (color, size, SKU, stock)
- **orders** - Customer orders with payment information
- **order_items** - Items within each order
- **subscriptions** - Newsletter subscriber emails
- **reviews** - Product reviews and ratings

## API Endpoints

### Authentication
- `GET /` - Home page with product listing
- `GET /register` - Registration page
- `POST /register` - Register new user
- `GET /login` - Login page
- `POST /login` - Authenticate user
- `GET /logout` - Logout user
- `GET /account` - User account dashboard

### Products & Shopping
- `GET /product/<id>` - Product detail page
- `GET /category/<name>` - Products by category
- `POST /add_to_cart/<id>` - Add product to cart
- `GET /cart` - View shopping cart
- `POST /update_cart/<key>` - Update item quantity
- `POST /remove_from_cart/<key>` - Remove item from cart

### Checkout & Orders
- `GET /checkout` - Checkout page
- `POST /checkout` - Process checkout
- `POST /orders` - Create order
- `GET /orders` - Order history

### Customer Engagement
- `GET /contact` - Contact form page
- `POST /contact` - Submit contact form
- `POST /subscribe` - Newsletter subscription
- `GET /customer_care` - Customer support page
- `POST /customer_care` - AI chat support

### Admin
- `GET /support` - Support dashboard (shop owner only)

### Health
- `GET /health` - Application health check

## Configuration Details

### Security
- **Password Hashing**: PBKDF2-HMAC-SHA256 with 200,000 iterations
- **Session Secret**: Required for session encryption
- **HTTPS**: Recommended for production deployments

### Email Configuration
For Gmail:
1. Enable 2-factor authentication on your Google account
2. Generate an app-specific password: https://myaccount.google.com/apppasswords
3. Use the app password in `SMTP_PASS`

For other providers, adjust `SMTP_SERVER` and `SMTP_PORT` accordingly.

### Razorpay Integration
1. Create a Razorpay account: https://razorpay.com
2. Get your API keys from the dashboard
3. Set `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET`
4. Payments are optional; the app works without them

### Groq AI Integration
1. Sign up for free at https://console.groq.com
2. Get your API key from the dashboard
3. Set `GROQ_API_KEY` and choose a model (default: `mixtral-8x7b-32768`)
4. AI support is optional; contact forms work without it

## Troubleshooting

### Database Issues
```bash
# Reset the database
rm nocap.db
python -c "from src.db import init_database; init_database()"
```

### Port Already in Use
```bash
# Use a different port
uvicorn app:app --port 8001
```

### Missing Environment Variables
The app will run with defaults for most variables. If a feature doesn't work:
1. Check the `.env` file has all required variables
2. Restart the development server after updating `.env`
3. For optional features, check the error logs

### Email Not Sending
- Verify SMTP credentials in `.env`
- Check that the Gmail app password is correct (not your regular password)
- Ensure 2FA is enabled on Gmail
- Check firewall/antivirus isn't blocking SMTP port 587

### Tests Failing
```bash
# Run with verbose output
python -m pytest tests/ -v --tb=short

# Run a specific test
python -m pytest tests/test_auth_routes.py::TestLoginRoute::test_login_success -v
```

## Development Tips

### Hot Reload
The `--reload` flag enables automatic restart on code changes:
```bash
uvicorn app:app --reload
```

### Debug Mode
Add print statements or use a debugger:
```bash
# Using pdb
import pdb; pdb.set_trace()
```

### Database Queries
Check `src/db.py` for all database operations. Most functions handle connection management automatically.

### Session Management
User sessions are managed via Starlette's SessionMiddleware. Cart data is stored in the session.

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests: `pytest tests/ -v`
4. Ensure all tests pass
5. Submit a pull request

## Deployment Checklist

- [ ] Set secure `SESSION_SECRET` (generate with: `python -c "import secrets; print(secrets.token_urlsafe())"`)
- [ ] Configure email settings (SMTP_SERVER, SMTP_USER, SMTP_PASS)
- [ ] Configure Razorpay keys (if using payments)
- [ ] Configure Groq API key (if using AI support)
- [ ] Run database initialization
- [ ] Test payment flow in sandbox mode
- [ ] Enable HTTPS in production
- [ ] Configure CORS if needed
- [ ] Run full test suite
- [ ] Set up monitoring and logging

## License

Proprietary - NoCaps E-Commerce Platform

## Support

For issues or questions, use the contact form in the application or create an issue in the repository.

## Changelog

### Version 1.0.0
- Initial release
- Complete e-commerce platform with product catalog
- User authentication and account management
- Shopping cart and checkout
- Order management
- Newsletter subscriptions
- Contact forms
- AI-powered customer support
- Payment gateway integration
- Comprehensive test suite (183 tests)
