"""API v1 router"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    products_router,
    categories_router,
    store_products_router
)

router = APIRouter(prefix="/v1")

# Include all endpoint routers
router.include_router(products_router)
router.include_router(categories_router)
router.include_router(store_products_router)
