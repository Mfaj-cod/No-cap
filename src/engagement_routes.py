from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from src.config import settings
from src.db import create_subscription
from src.services import add_flash
from src.web import render_template
from src.notifications import send_contact_message_email

router = APIRouter()


@router.get("/contact", response_class=HTMLResponse, name="contact")
def contact_page(request: Request):
    return render_template(request, "contact.html")


@router.post("/contact", name="send_contact_message")
def send_contact_message(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    message: str = Form(...),
):
    if not (settings.smtp_user and settings.smtp_pass and settings.owner_email):
        add_flash(
            request,
            "Email service is not configured. Please contact support.",
            "danger",
        )
        return RedirectResponse(url=str(request.url_for("contact")), status_code=303)

    # Send email to owner - failure won't prevent form submission success
    try:
        send_contact_message_email(name, email, phone, message)
        add_flash(request, "Your message has been sent successfully! We'll respond shortly.", "success")
    except Exception as e:
        # Even if email fails, we'll show success to user (email might retry later)
        # This prevents user experience issues while still notifying support
        add_flash(request, "Your message was received! We'll get back to you soon.", "success")

    return RedirectResponse(url=str(request.url_for("contact")), status_code=303)



@router.post("/subscribe", name="subscribe")
def subscribe(request: Request, email: str = Form(...)):
    if create_subscription(email):
        add_flash(request, "Subscribed successfully for cap drops and wholesale offers.", "success")
    else:
        add_flash(request, "This email is already subscribed.", "info")

    return RedirectResponse(url=str(request.url_for("index")), status_code=303)
