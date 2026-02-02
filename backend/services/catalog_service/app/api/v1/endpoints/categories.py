"""Category endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.services import CategoryService
from app.api.v1.schemas.catalog import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    StandardResponse
)

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new category"""
    try:
        service = CategoryService(db)
        new_category = await service.create_category(category)
        return new_category
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create category: {str(e)}"
        )


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get category by ID"""
    service = CategoryService(db)
    category = await service.get_category(category_id)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return category


@router.get("/slug/{slug}", response_model=CategoryResponse)
async def get_category_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """Get category by slug"""
    service = CategoryService(db)
    category = await service.get_category_by_slug(slug)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    category_update: CategoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update category"""
    service = CategoryService(db)
    category = await service.update_category(category_id, category_update)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return category


@router.delete("/{category_id}", response_model=StandardResponse)
async def delete_category(
    category_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete category (soft delete)"""
    service = CategoryService(db)
    success = await service.delete_category(category_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return StandardResponse(
        success=True,
        message="Category deleted successfully"
    )


@router.get("/", response_model=list[CategoryResponse])
async def list_categories(
    parent_id: Optional[str] = Query(None, description="Filter by parent category"),
    db: AsyncSession = Depends(get_db)
):
    """List all categories, optionally filtered by parent"""
    service = CategoryService(db)
    categories = await service.list_categories(parent_id=parent_id)
    return categories
