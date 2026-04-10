import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

test_key_id = "rzp_test_SZutUFttWN5nHT"
test_key_secret = "fQwjH6avXXG3W9BlXshGpKPp"

print("Testing Razorpay credentials...")

if not test_key_id or not test_key_secret:
    print("Test credentials missing")
    exit(1)

try:
    import razorpay
    print("razorpay module imported successfully")
    
    client = razorpay.Client(auth=(test_key_id, test_key_secret))
    print("Razorpay client initialized")
    
    print("Creating test order...")
    order = client.order.create({
        "amount": 5000,
        "currency": "INR",
        "receipt": "test_order_001",
    })
    print("Test order created successfully!")
    print(f"Order ID: {order['id']}")
    print(f"Amount: {order['amount'] / 100} INR")
    
except ImportError as e:
    print(f"Failed to import razorpay: {e}")
    exit(1)
    
except Exception as e:
    print(f"Razorpay API error: {e}")
    print(f"Type: {type(e).__name__}")
    exit(1)

print("All tests passed!")
