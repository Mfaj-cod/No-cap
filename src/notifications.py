import smtplib
from email.mime.text import MIMEText
from typing import Optional

from src.config import settings
from src.db import get_order


def _send_mail(subject: str, body: str, recipient: str) -> None:
    if not (settings.smtp_user and settings.smtp_pass and settings.smtp_server and settings.owner_email):
        print("SMTP not configured; skipping email to", recipient)
        return

    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = settings.smtp_user
        msg["To"] = recipient

        server = smtplib.SMTP(settings.smtp_server, settings.smtp_port)
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_pass)
        server.send_message(msg)
        server.quit()
        print("Email sent to", recipient)
    except Exception as exc:
        print("Failed to send email to", recipient, exc)


def send_order_placed_email(order_id: int) -> None:
    order = get_order(order_id)
    if not order:
        return
    subject = f"Your NoCaps order #{order_id} has been received"
    lines = [
        f"Hi {order.get('name')},",
        "",
        f"Thanks — we received your order #{order_id}. Here are the details:",
    ]
    for item in order.get("items", []):
        lines.append(f" - {item['product_name']} x{item['quantity']} @ Rs. {item['applied_unit_price']}")
    lines += [
        "",
        f"Total: Rs. {order.get('total')}",
        f"Delivery address: {order.get('address')}, {order.get('city')} - {order.get('pincode')}",
        "",
        "We'll update you when your order ships.",
        "Thanks,",
        "NoCaps team",
    ]
    body = "\n".join(lines)
    _send_mail(subject, body, order.get("email") or settings.owner_email)


def send_order_delivered_email(order_id: int) -> None:
    order = get_order(order_id)
    if not order:
        return
    subject = f"Your NoCaps order #{order_id} has been delivered"
    body = (
        f"Hi {order.get('name')},\n\nYour order #{order_id} has been marked delivered. Thank you for shopping with NoCaps!\n\n"
        "If you have any issues, please contact support.\n\nThanks,\nNoCaps team"
    )
    _send_mail(subject, body, order.get("email") or settings.owner_email)


def send_password_reset_otp_email(email: str, otp: str) -> None:
    """Send password reset OTP to user's email"""
    subject = "Your NoCaps Password Reset OTP"
    body = (
        f"Hi there,\n\n"
        f"We received a request to reset your password for your NoCaps account.\n"
        f"Use the following One-Time Password (OTP) to proceed:\n\n"
        f"OTP: {otp}\n\n"
        f"This OTP will expire in 10 minutes.\n\n"
        f"If you did not request this, please ignore this email.\n\n"
        f"Thanks,\nNoCaps team"
    )
    _send_mail(subject, body, email)
