from fastapi import APIRouter, Request, Request
from fastapi.responses import HTMLResponse

from src.web import render_template

router = APIRouter()

@router.get("/privacy", response_class=HTMLResponse, name="privacy_policy")
def privacy_policy(request: Request):
    return render_template(request, "privacy_policy.html")


@router.get("/terms", response_class=HTMLResponse, name="terms_of_service")
def terms_of_service(request: Request):
    return render_template(request, "terms_of_service.html")