from datetime import datetime

from fastapi import Request
from fastapi.templating import Jinja2Templates

from src.config import settings
from src.data import WHOLESALE_DISCOUNT
from src.services import cart_item_count, get_current_user, pop_flash_messages
import os

# collect first 40 images from static/img for gallery/fallback
def _collect_gallery_images(limit: int = 40):
    """Collect image paths under the project's static/img directory.

    Use the package file location (not os.getcwd()) so discovery works
    regardless of the current working directory when the app runs.
    Returns paths relative to the `static/` folder, suitable for
    `url_for('static', path=...)`.
    """
    from pathlib import Path

    images = []
    project_root = Path(__file__).resolve().parents[1]
    static_dir = project_root / "static"
    root = static_dir / "img"
    exts = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
    if not root.is_dir():
        return images

    for p in sorted(root.rglob('*')):
        if p.is_file() and p.suffix.lower() in exts:
            try:
                rel = p.relative_to(static_dir).as_posix()
            except Exception:
                # fallback to manual relpath
                rel = os.path.relpath(str(p), str(static_dir)).replace('\\', '/')
            images.append(rel)
            if len(images) >= limit:
                break

    return images




def money(value: float) -> str:
    return f"Rs. {value:,.2f}"


templates = Jinja2Templates(directory="templates")
templates.env.cache = {}  # reset cache explicitly
templates.env.filters["money"] = money


def render_template(request: Request, template_name: str, **context):
    # print("TEMPLATE_NAME:", template_name, type(template_name))
    if not isinstance(template_name, str):
        raise ValueError(f"Template name is NOT string: {template_name}")
    
    base_context = {
        "request": request,
        "flash_messages": pop_flash_messages(request),
        "current_user": get_current_user(request),
        "cart_count": cart_item_count(request),
        "store_name": settings.store_name,
        "current_year": datetime.now().year,
        "wholesale_discount_percent": int(WHOLESALE_DISCOUNT * 100),
        # pre-load a small gallery of images from static/img to use as fallbacks
        "gallery_images": _collect_gallery_images(40),
    }
    base_context.update(context)
    return templates.TemplateResponse(name=template_name, context=base_context)
