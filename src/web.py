from datetime import datetime

from fastapi import Request
from fastapi.templating import Jinja2Templates

from src.config import settings
from src.data import WHOLESALE_DISCOUNT
from src.services import cart_item_count, get_current_user, pop_flash_messages

templates = Jinja2Templates(directory="templates")


def money(value: float) -> str:
    return f"Rs. {value:,.2f}"


templates.env.filters["money"] = money


def render_template(request: Request, template_name: str, **context):
    base_context = {
        "request": request,
        "flash_messages": pop_flash_messages(request),
        "current_user": get_current_user(request),
        "cart_count": cart_item_count(request),
        "store_name": settings.store_name,
        "current_year": datetime.now().year,
        "wholesale_discount_percent": int(WHOLESALE_DISCOUNT * 100),
    }
    base_context.update(context)
    return templates.TemplateResponse(template_name, base_context)
