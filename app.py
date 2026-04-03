from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from src.config import settings
from src.db import init_database
from src.auth_routes import router as auth_router
from src.cart_routes import router as cart_router
from src.engagement_routes import router as engagement_router
from src.orders_routes import router as orders_router
from src.storefront_routes import router as storefront_router
from src.support_routes import router as support_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_database()
    yield


app = FastAPI(title="Apna Swad Caps", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(storefront_router)
app.include_router(auth_router)
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(engagement_router)
app.include_router(support_router)


@app.get("/health", name="healthcheck")
def healthcheck():
    return {"status": "ok"}
