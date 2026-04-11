import sqlite3
import random
import string

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from src.db import (
    create_user,
    get_user_by_email,
    list_orders_for_user,
    store_reset_otp,
    verify_reset_otp,
    reset_user_password,
    clear_reset_otp,
)
from src.security import hash_password, verify_password
from src.services import add_flash, get_current_user, login_user, logout_user
from src.web import render_template
from src.notifications import send_password_reset_otp_email

router = APIRouter()


@router.get("/register", response_class=HTMLResponse, name="register")
def register_page(request: Request):
    return render_template(request, "register.html")


@router.post("/register", name="register_user")
def register_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    role: str = Form(...),
):
    if role not in {"customer", "shop_owner"}:
        add_flash(request, "Please choose a valid account type.", "danger")
        return RedirectResponse(url=str(request.url_for("register")), status_code=303)

    if password != confirm_password:
        add_flash(request, "Passwords do not match.", "danger")
        return RedirectResponse(url=str(request.url_for("register")), status_code=303)

    if len(password) < 6:
        add_flash(request, "Use at least 6 characters for your password.", "danger")
        return RedirectResponse(url=str(request.url_for("register")), status_code=303)

    try:
        create_user(name, email, hash_password(password), role)
    except sqlite3.IntegrityError:
        add_flash(request, "An account with that email already exists.", "danger")
        return RedirectResponse(url=str(request.url_for("register")), status_code=303)

    user = get_user_by_email(email)
    if user:
        login_user(request, user)

    add_flash(request, "Your account is ready. Welcome to the cap store.", "success")
    return RedirectResponse(url=str(request.url_for("account")), status_code=303)


@router.get("/login", response_class=HTMLResponse, name="login")
def login_page(request: Request):
    return render_template(request, "login.html")


@router.post("/login", name="login_user")
def login_account(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
):
    user = get_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        add_flash(request, "Invalid email or password.", "danger")
        return RedirectResponse(url=str(request.url_for("login")), status_code=303)

    # Auto-promote fajalmoaj@gmail.com to admin role
    if email.lower() == "fajalmoaj@gmail.com" and user["role"] != "admin":
        from src.db import get_connection
        conn = get_connection()
        conn.execute("UPDATE users SET role = 'admin' WHERE id = ?", (user["id"],))
        conn.commit()
        conn.close()
        user["role"] = "admin"

    login_user(request, user)
    add_flash(request, f"Welcome back, {user['name']}.", "success")
    return RedirectResponse(url=str(request.url_for("account")), status_code=303)


@router.get("/logout", name="logout")
def logout(request: Request):
    logout_user(request)
    add_flash(request, "You have been logged out.", "info")
    return RedirectResponse(url=str(request.url_for("index")), status_code=303)


@router.get("/account", response_class=HTMLResponse, name="account")
def account(request: Request):
    current_user = get_current_user(request)
    if not current_user:
        add_flash(request, "Please log in to view your account.", "info")
        return RedirectResponse(url=str(request.url_for("login")), status_code=303)

    return render_template(
        request,
        "account.html",
        orders=list_orders_for_user(current_user["id"]),
    )


@router.get("/forgot-password", response_class=HTMLResponse, name="forgot_password")
def forgot_password_page(request: Request):
    return render_template(request, "forgot_password.html")


@router.post("/forgot-password", name="request_password_reset")
def request_password_reset(
    request: Request,
    email: str = Form(...),
):
    user = get_user_by_email(email)
    if not user:
        # Don't reveal if email exists for security reasons
        add_flash(
            request,
            "If that email exists in our system, you'll receive a password reset link.",
            "info",
        )
        return RedirectResponse(url=str(request.url_for("login")), status_code=303)

    # Generate OTP (6 digits)
    otp = "".join(random.choices(string.digits, k=6))
    
    # Store OTP in database
    if store_reset_otp(email, otp):
        # Send OTP email in background (won't block - user can resend if needed)
        send_password_reset_otp_email(email, otp)
        add_flash(request, "OTP has been sent to your email. Check your inbox.", "info")
        
        # Store email in session for next step
        request.session["reset_email"] = email
        return RedirectResponse(url=str(request.url_for("verify_otp")), status_code=303)
    else:
        add_flash(request, "An error occurred. Please try again later.", "danger")
        return RedirectResponse(url=str(request.url_for("forgot_password")), status_code=303)


@router.get("/verify-otp", response_class=HTMLResponse, name="verify_otp")
def verify_otp_page(request: Request):
    email = request.session.get("reset_email")
    if not email:
        add_flash(request, "Please request a password reset first.", "info")
        return RedirectResponse(url=str(request.url_for("forgot_password")), status_code=303)
    
    return render_template(request, "verify_otp.html", email=email)


@router.post("/verify-otp", name="verify_otp_submit")
def verify_otp_submit(
    request: Request,
    otp: str = Form(...),
):
    email = request.session.get("reset_email")
    if not email:
        add_flash(request, "Please request a password reset first.", "info")
        return RedirectResponse(url=str(request.url_for("forgot_password")), status_code=303)
    
    if verify_reset_otp(email, otp):
        add_flash(request, "OTP verified successfully. Please set your new password.", "success")
        request.session["otp_verified"] = True
        return RedirectResponse(url=str(request.url_for("reset_password")), status_code=303)
    else:
        add_flash(request, "Invalid or expired OTP. Please try again.", "danger")
        return RedirectResponse(url=str(request.url_for("verify_otp")), status_code=303)


@router.get("/reset-password", response_class=HTMLResponse, name="reset_password")
def reset_password_page(request: Request):
    email = request.session.get("reset_email")
    otp_verified = request.session.get("otp_verified", False)
    
    if not email or not otp_verified:
        add_flash(request, "Please verify your OTP first.", "info")
        return RedirectResponse(url=str(request.url_for("verify_otp")), status_code=303)
    
    return render_template(request, "reset_password.html")


@router.post("/reset-password", name="reset_password_submit")
def reset_password_submit(
    request: Request,
    new_password: str = Form(...),
    confirm_password: str = Form(...),
):
    email = request.session.get("reset_email")
    otp_verified = request.session.get("otp_verified", False)
    
    if not email or not otp_verified:
        add_flash(request, "Please verify your OTP first.", "info")
        return RedirectResponse(url=str(request.url_for("verify_otp")), status_code=303)
    
    if new_password != confirm_password:
        add_flash(request, "Passwords do not match.", "danger")
        return RedirectResponse(url=str(request.url_for("reset_password")), status_code=303)
    
    if len(new_password) < 6:
        add_flash(request, "Use at least 6 characters for your password.", "danger")
        return RedirectResponse(url=str(request.url_for("reset_password")), status_code=303)
    
    # Reset password
    hashed_password = hash_password(new_password)
    if reset_user_password(email, hashed_password):
        # Clear session
        request.session.pop("reset_email", None)
        request.session.pop("otp_verified", None)
        add_flash(request, "Password has been reset successfully. Please log in with your new password.", "success")
        return RedirectResponse(url=str(request.url_for("login")), status_code=303)
    else:
        add_flash(request, "An error occurred while resetting password. Please try again.", "danger")
        return RedirectResponse(url=str(request.url_for("reset_password")), status_code=303)
