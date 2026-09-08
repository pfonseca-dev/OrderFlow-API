from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.order import router as order_router
from app.api.routes.products import router as product_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(product_router)
api_router.include_router(order_router)
