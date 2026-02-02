"""Store-Product association endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.services import StoreProductService
from app.api.v1.schemas.catalog import (
    StoreProductCreate,
    StoreProductUpdate,
    StoreProductResponse,
    StandardResponse
)

router = APIRouter(prefix="/store-products", tags=["Store Products"])


@router.post("/", response_model=StoreProductResponse, status_code=status.HTTP_201_CREATED)
async def add_product_to_store(
    store_product: StoreProductCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a product to a store's inventory"""
    try:
        service = StoreProductService(db)
        new_store_product = await service.add_product_to_store(store_product)
        return new_store_product
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add product to store: {str(e)}"
        )


@router.get("/{store_product_id}", response_model=StoreProductResponse)
async def get_store_product(
    store_product_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get store product by ID"""
    service = StoreProductService(db)
    store_product = await service.get_store_product(store_product_id)
    
    if not store_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store product not found"
        )
    
    return store_product


@router.put("/{store_product_id}")
async def update_store_product(
    store_product_id: str,
    store_product_update: StoreProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update store product (stock, price, availability)"""
    service = StoreProductService(db)
    result = await service.update_store_product(store_product_id, store_product_update)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store product not found"
        )
    
    return result


@router.delete("/{store_product_id}", response_model=StandardResponse)
async def remove_product_from_store(
    store_product_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Remove product from store (soft delete)"""
    service = StoreProductService(db)
    success = await service.remove_product_from_store(store_product_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store product not found"
        )
    
    return StandardResponse(
        success=True,
        message="Product removed from store successfully"
    )


@router.get("/store/{store_id}", response_model=list[StoreProductResponse])
async def list_store_products(
    store_id: str,
    is_available: Optional[bool] = Query(None),
    category_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List all products for a specific store"""
    service = StoreProductService(db)
    products, total = await service.list_store_products(
        store_id=store_id,
        is_available=is_available,
        category_id=category_id,
        page=page,
        page_size=page_size
    )
    
    return products
