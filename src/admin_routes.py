from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

from src.services import get_current_user
from src.web import render_template
from src.db import list_orders, update_order_status, get_order
from src.notifications import send_order_delivered_email

router = APIRouter()


def _require_admin(request: Request):
    user = get_current_user(request)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.get("/admin/orders", response_class=HTMLResponse, name="admin_orders")
def admin_orders_page(request: Request):
    _require_admin(request)
    orders = list_orders(50)
    return render_template(request, "admin_orders.html", orders=orders)


@router.get("/api/admin/orders", response_class=JSONResponse)
def api_list_orders(request: Request):
    _require_admin(request)
    orders = [o for o in list_orders(200) if o.get("status") not in ("cancelled", "failed")]
    # sanitize/shape minimal data
    out = []
    for o in orders:
        out.append(
            {
                "id": o["id"],
                "name": o["name"],
                "email": o["email"],
                "address": ", ".join(filter(None, [
                    o.get("address"),
                    o.get("city"),
                    o.get("pincode")
                ])),
                "status": o.get("status"),
                "payment_method": o.get("payment_method"),
                "total": o.get("total"),
                "items": o.get("items", []),
                "created_at": o.get("created_at"),
            }
        )
    return JSONResponse(out)


@router.post("/api/admin/orders/{order_id}/status", response_class=JSONResponse)
async def api_update_order_status(request: Request, order_id: int):
    _require_admin(request)
    payload = await request.json()
    new_status = payload.get("status") if isinstance(payload, dict) else None
    if not new_status:
        return JSONResponse({"error": "Missing status"}, status_code=400)

    # apply update
    update_order_status(order_id, new_status)

    # on delivered, send customer email
    if new_status in ("delivered", "order delivered"):
        try:
            send_order_delivered_email(order_id)
        except Exception:
            pass

    order = get_order(order_id)
    return JSONResponse({"success": True, "order": order})
