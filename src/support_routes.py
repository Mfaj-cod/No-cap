from pydantic import BaseModel

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse

from src.ai_support import generate_support_response
from src.web import render_template

router = APIRouter()


class SupportMessage(BaseModel):
    message: str


@router.get("/customer-care", response_class=HTMLResponse, name="customer_care_page")
def customer_care_page(request: Request):
    return render_template(request, "customer_care.html")


@router.post("/customer-care/message", name="customer_care_message")
def customer_care_message(payload: SupportMessage):
    message = payload.message.strip()
    if not message:
        return JSONResponse({"error": "Please enter a message first."}, status_code=400)

    try:
        answer = generate_support_response(message)
    except RuntimeError as exc:
        return JSONResponse({"error": str(exc)}, status_code=503)
    except Exception:
        return JSONResponse(
            {"error": "The customer care assistant is temporarily unavailable. Please try again shortly."},
            status_code=503,
        )

    return JSONResponse({"answer": answer})
