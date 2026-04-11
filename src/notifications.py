import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.config import settings
from src.db import get_order

logger = logging.getLogger(__name__)


def _get_html_wrapper(content: str) -> str:
    """Wrap email content in NoCaps branded HTML template"""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                background: linear-gradient(135deg, #07111d 0%, #0f172a 100%);
                color: #f8fafc;
                line-height: 1.6;
            }}
            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                background: rgba(10, 18, 32, 0.95);
                border: 1px solid rgba(255, 193, 7, 0.2);
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
            }}
            .email-header {{
                background: linear-gradient(135deg, rgba(255, 193, 7, 0.15), rgba(255, 193, 7, 0.05));
                padding: 30px 24px;
                border-bottom: 1px solid rgba(255, 193, 7, 0.2);
                text-align: center;
            }}
            .brand {{
                font-size: 28px;
                font-weight: 800;
                color: white;
                margin-bottom: 8px;
            }}
            .brand-accent {{
                color: #ffc107;
            }}
            .email-body {{
                padding: 32px 24px;
            }}
            h2 {{
                color: #ffc107;
                font-size: 20px;
                margin-bottom: 16px;
                font-weight: 700;
            }}
            p {{
                color: #cbd5e1;
                margin-bottom: 12px;
                font-size: 14px;
            }}
            .order-details {{
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 193, 7, 0.15);
                border-radius: 12px;
                padding: 20px;
                margin: 20px 0;
            }}
            .detail-row {{
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid rgba(255, 193, 7, 0.1);
                color: #cbd5e1;
                font-size: 14px;
            }}
            .detail-row:last-child {{
                border-bottom: none;
            }}
            .detail-label {{
                color: #9fb0c3;
                font-weight: 600;
            }}
            .total-amount {{
                font-size: 18px;
                font-weight: 700;
                color: #ffc107;
                text-align: center;
                padding-top: 12px;
                border-top: 1px solid rgba(255, 193, 7, 0.15);
            }}
            .otp-box {{
                background: rgba(255, 193, 7, 0.1);
                border: 2px solid #ffc107;
                border-radius: 8px;
                padding: 20px;
                text-align: center;
                margin: 20px 0;
            }}
            .otp-code {{
                font-size: 32px;
                font-weight: 800;
                color: #ffc107;
                letter-spacing: 4px;
                font-family: monospace;
            }}
            .cta-button {{
                display: inline-block;
                background: linear-gradient(135deg, #ffd54c, #ffc107);
                color: #09111b;
                padding: 12px 28px;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 700;
                font-size: 14px;
                margin: 20px 0;
            }}
            .email-footer {{
                background: rgba(255, 255, 255, 0.03);
                padding: 24px;
                border-top: 1px solid rgba(255, 193, 7, 0.1);
                text-align: center;
                color: #9fb0c3;
                font-size: 12px;
            }}
            .footer-text {{
                margin-bottom: 8px;
            }}
            .social {{
                margin-top: 12px;
                font-size: 12px;
            }}
            ul {{
                list-style: none;
                margin: 16px 0;
            }}
            li {{
                color: #cbd5e1;
                padding: 8px 0;
                border-bottom: 1px solid rgba(255, 193, 7, 0.08);
                font-size: 14px;
            }}
            li:last-child {{
                border-bottom: none;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="email-header">
                <div class="brand">NO<span class="brand-accent">Cap</span></div>
                <p style="color: #9fb0c3; margin: 0; font-size: 13px;">Premium Caps for Everyone</p>
            </div>
            {content}
            <div class="email-footer">
                <div class="footer-text">© 2024 NoCaps. All rights reserved.</div>
                <div class="footer-text">Questions? Reply to this email or visit our website.</div>
            </div>
        </div>
    </body>
    </html>
    """


def _send_email(recipient: str, subject: str, html_content: str) -> None:
    """Send email using SMTP - won't raise exceptions if delivery fails"""
    if not (settings.smtp_user and settings.smtp_pass and settings.smtp_server and settings.owner_email):
        logger.warning(f"SMTP not configured; skipping email to {recipient}")
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.smtp_user
        msg["To"] = recipient
        
        # Attach HTML
        msg.attach(MIMEText(html_content, "html"))
        
        server = smtplib.SMTP(settings.smtp_server, settings.smtp_port)
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_pass)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email sent successfully to {recipient}")
    except Exception as exc:
        logger.error(f"Failed to send email to {recipient}: {type(exc).__name__}: {exc}", exc_info=True)
        # Don't re-raise - let the order go through even if email fails


def send_order_placed_email(order_id: int) -> None:
    """Send order confirmation email with order details"""
    order = get_order(order_id)
    if not order:
        return

    recipient = order.get("email") or settings.owner_email
    subject = f"Order #{order_id} Confirmed - NoCaps"

    items_html = "\n".join(
        [
            f"<li><strong>{item['product_name']}</strong> × {item['quantity']} @ Rs. {item['applied_unit_price']}</li>"
            for item in order.get("items", [])
        ]
    )

    content = f"""
    <div class="email-body">
        <h2>Order Confirmed! 🎉</h2>
        <p>Hi <strong>{order.get('name')}</strong>,</p>
        <p>Thank you for your order! We've received it and are getting it ready for you.</p>
        
        <div class="order-details">
            <div class="detail-row">
                <span class="detail-label">Order ID</span>
                <span>#{order_id}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Status</span>
                <span>{order.get('status', 'Pending').title()}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Payment</span>
                <span>{order.get('payment_method', 'N/A').upper()}</span>
            </div>
        </div>

        <h2 style="margin-top: 24px;">Order Items</h2>
        <ul>{items_html}</ul>

        <div class="order-details">
            <div class="detail-row">
                <span class="detail-label">Subtotal</span>
                <span>Rs. {order.get('subtotal', 0)}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Discount</span>
                <span>-Rs. {order.get('discount', 0)}</span>
            </div>
            <div class="total-amount">Total: Rs. {order.get('total')}</div>
        </div>

        <h2 style="margin-top: 24px;">Delivery Address</h2>
        <p style="background: rgba(255, 193, 7, 0.05); padding: 12px; border-radius: 8px; color: #cbd5e1;">
            {order.get('address')}<br>
            {order.get('city')} - {order.get('pincode')}<br>
            📞 {order.get('phone')}
        </p>

        <p style="margin-top: 24px; color: #9fb0c3;">We'll notify you when your order ships. Track your delivery in real-time once it's on the way!</p>
    </div>
    """

    html = _get_html_wrapper(content)
    _send_email(recipient, subject, html)


def send_order_delivered_email(order_id: int) -> None:
    """Send order delivered notification"""
    order = get_order(order_id)
    if not order:
        return

    recipient = order.get("email") or settings.owner_email
    subject = f"Order #{order_id} Delivered - NoCaps"

    content = f"""
    <div class="email-body">
        <h2>Order Delivered! 📦</h2>
        <p>Hi <strong>{order.get('name')}</strong>,</p>
        <p>Great news! Your order has been delivered successfully.</p>

        <div class="order-details">
            <div class="detail-row">
                <span class="detail-label">Order ID</span>
                <span>#{order_id}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Total Amount</span>
                <span style="color: #ffc107; font-weight: 700;">Rs. {order.get('total')}</span>
            </div>
        </div>

        <p style="margin-top: 24px; color: #cbd5e1;">
            Thank you for shopping with <strong>NoCaps</strong>! We hope you enjoy your caps.
        </p>
        <p style="color: #9fb0c3; font-size: 13px;">
            Have any issues? Our support team is always here to help. Reply to this email or contact us.
        </p>
    </div>
    """

    html = _get_html_wrapper(content)
    _send_email(recipient, subject, html)


def send_password_reset_otp_email(email: str, otp: str) -> None:
    """Send password reset OTP with styled template"""
    subject = "Reset Your NoCaps Password"

    content = f"""
    <div class="email-body">
        <h2>Password Reset Request</h2>
        <p>Hi there,</p>
        <p>We received a request to reset your NoCaps account password. Use the code below to proceed:</p>

        <div class="otp-box">
            <p style="color: #9fb0c3; margin-bottom: 8px; font-size: 13px;">Your One-Time Password</p>
            <div class="otp-code">{otp}</div>
            <p style="color: #9fb0c3; margin-top: 12px; font-size: 12px;">Valid for 10 minutes</p>
        </div>

        <p style="color: #cbd5e1;">Enter this code in the password reset form to create a new password.</p>
        <p style="color: #9fb0c3; font-size: 13px;">Didn't request this? You can safely ignore this email. Your account remains secure.</p>
    </div>
    """

    html = _get_html_wrapper(content)
    _send_email(email, subject, html)


def send_contact_message_email(name: str, email: str, phone: str, message: str) -> None:
    """Send contact form submission to owner with styled template"""
    subject = f"New Message from {name} - NoCaps Contact Form"

    content = f"""
    <div class="email-body">
        <h2>New Customer Message 📨</h2>
        <p>You have a new message from a customer:</p>

        <div class="order-details">
            <div class="detail-row">
                <span class="detail-label">Name</span>
                <span>{name}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Email</span>
                <span>{email}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Phone</span>
                <span>{phone}</span>
            </div>
        </div>

        <h2 style="margin-top: 24px;">Message</h2>
        <p style="background: rgba(255, 193, 7, 0.05); padding: 12px; border-radius: 8px; white-space: pre-wrap; color: #cbd5e1;">{message}</p>

        <p style="margin-top: 24px; color: #9fb0c3; font-size: 13px;">Reply to this email to respond to the customer.</p>
    </div>
    """

    html = _get_html_wrapper(content)
    _send_email(settings.owner_email, subject, html)
