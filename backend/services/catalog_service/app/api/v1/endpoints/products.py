"""Product endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from decimal import Decimal

from app.database import get_db
from app.services import ProductService
from app.api.v1.schemas.catalog import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductSearchResponse,
    StandardResponse
)

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new product"""
    try:
        service = ProductService(db)
        new_product = await service.create_product(product)
        return new_product
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create product: {str(e)}"
        )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get product by ID"""
    service = ProductService(db)
    product = await service.get_product(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product_update: ProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update product"""
    service = ProductService(db)
    product = await service.update_product(product_id, product_update)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product


@router.delete("/{product_id}", response_model=StandardResponse)
async def delete_product(
    product_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete product (soft delete)"""
    service = ProductService(db)
    success = await service.delete_product(product_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return StandardResponse(
        success=True,
        message="Product deleted successfully"
    )


@router.get("/", response_model=ProductSearchResponse)
async def list_products(
    category_id: Optional[str] = Query(None),
    min_price: Optional[Decimal] = Query(None, ge=0),
    max_price: Optional[Decimal] = Query(None, ge=0),
    is_active: Optional[bool] = Query(True),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List products with filters"""
    service = ProductService(db)
    products, total = await service.list_products(
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        is_active=is_active,
        page=page,
        page_size=page_size
    )
    
    return ProductSearchResponse(
        products=products,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/search/", response_model=ProductSearchResponse)
async def search_products(
    q: str = Query(..., min_length=2, description="Search query"),
    category_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Full-text search for products"""
    service = ProductService(db)
    products, total = await service.search_products(
        search_query=q,
        category_id=category_id,
        page=page,
        page_size=page_size
    )
    
    return ProductSearchResponse(
        products=products,
        total=total,
        page=page,
        page_size=page_size
    )
