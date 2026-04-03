import smtplib
from email.mime.text import MIMEText

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from src.config import settings
from src.db import create_subscription
from src.services import add_flash
from src.web import render_template

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
            "Contact email is not configured yet. Please update the SMTP settings first.",
            "danger",
        )
        return RedirectResponse(url=str(request.url_for("contact")), status_code=303)

    body = (
        f"New website enquiry from Apna Swad Caps\n\n"
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Phone: {phone}\n\n"
        f"Message:\n{message}"
    )

    try:
        email_message = MIMEText(body)
        email_message["Subject"] = f"New customer message from {name}"
        email_message["From"] = settings.smtp_user
        email_message["To"] = settings.owner_email

        server = smtplib.SMTP(settings.smtp_server, settings.smtp_port)
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_pass)
        server.send_message(email_message)
        server.quit()
        add_flash(request, "Your message has been sent successfully.", "success")
    except Exception:
        add_flash(request, "We could not send your message right now. Please try again later.", "danger")

    return RedirectResponse(url=str(request.url_for("contact")), status_code=303)


@router.post("/subscribe", name="subscribe")
def subscribe(request: Request, email: str = Form(...)):
    if create_subscription(email):
        add_flash(request, "Subscribed successfully for cap drops and wholesale offers.", "success")
    else:
        add_flash(request, "This email is already subscribed.", "info")

    return RedirectResponse(url=str(request.url_for("index")), status_code=303)
