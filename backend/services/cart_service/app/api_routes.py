from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from app.database import get_db
from app.models import Cart, CartItem
from app.schemas import (
    CartCreate, CartResponse, CartDetailedResponse,
    CartItemCreate, CartItemUpdate, CartItemResponse,
    CartValidationResult, CheckoutRequest, CheckoutResponse,
    BulkAddRequest, BulkAddResponse
)
from app.services import CartService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/carts", tags=["carts"])


# ==================== Cart Operations ====================

@router.post("/", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def create_cart(
    request: CartCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new shopping cart for a customer"""
    try:
        service = CartService(db)
        cart = await service.create_cart(request.customer_id)
        return cart
    except Exception as e:
        logger.error(f"Error creating cart: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{cart_id}", response_model=CartDetailedResponse)
async def get_cart(
    cart_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get cart details with all items"""
    try:
        service = CartService(db)
        cart = await service.get_cart(cart_id)
        
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cart {cart_id} not found"
            )
        
        totals = service.calculate_cart_totals(cart)
        
        return {
            "id": str(cart.id),
            "customer_id": cart.customer_id,
            "items": [item.to_dict() for item in cart.items],
            "items_count": len(cart.items),
            "total_items": totals["total_items"],
            "total_amount": totals["total_amount"],
            "created_at": cart.created_at,
            "updated_at": cart.updated_at
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cart: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/customer/{customer_id}", response_model=CartDetailedResponse)
async def get_customer_active_cart(
    customer_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get customer's active cart"""
    try:
        service = CartService(db)
        cart = await service.get_active_cart(customer_id)
        
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No active cart for customer {customer_id}"
            )
        
        totals = service.calculate_cart_totals(cart)
        
        return {
            "id": str(cart.id),
            "customer_id": cart.customer_id,
            "items": [item.to_dict() for item in cart.items],
            "items_count": len(cart.items),
            "total_items": totals["total_items"],
            "total_amount": totals["total_amount"],
            "created_at": cart.created_at,
            "updated_at": cart.updated_at
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting customer cart: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{cart_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart(
    cart_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete entire cart"""
    try:
        service = CartService(db)
        success = await service.delete_cart(cart_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cart {cart_id} not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting cart: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{cart_id}/clear", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    cart_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Clear all items from cart"""
    try:
        service = CartService(db)
        cart = await service.get_cart(cart_id)
        
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cart {cart_id} not found"
            )
        
        await service.clear_cart(cart_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing cart: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==================== Cart Item Operations ====================

@router.post("/{cart_id}/items", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
async def add_item(
    cart_id: str,
    request: CartItemCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add item to cart"""
    try:
        service = CartService(db)
        item = await service.add_item(
            cart_id=cart_id,
            product_id=request.product_id,
            store_id=request.store_id,
            quantity=request.quantity,
            unit_price=request.unit_price,
            product_name=request.product_name,
            product_image_url=request.product_image_url
        )
        return item.to_dict()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error adding item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{cart_id}/items/bulk", response_model=BulkAddResponse, status_code=status.HTTP_201_CREATED)
async def bulk_add_items(
    cart_id: str,
    request: BulkAddRequest,
    db: AsyncSession = Depends(get_db)
):
    """Add multiple items to cart at once"""
    try:
        service = CartService(db)
        
        added_count = 0
        failed_count = 0
        errors = []
        
        for item_req in request.items:
            try:
                await service.add_item(
                    cart_id=cart_id,
                    product_id=item_req.product_id,
                    store_id=item_req.store_id,
                    quantity=item_req.quantity,
                    unit_price=item_req.unit_price,
                    product_name=item_req.product_name,
                    product_image_url=item_req.product_image_url
                )
                added_count += 1
            except Exception as e:
                failed_count += 1
                errors.append({
                    "product_id": item_req.product_id,
                    "error": str(e)
                })
        
        return {
            "cart_id": cart_id,
            "added_count": added_count,
            "failed_count": failed_count,
            "errors": errors if errors else None
        }
    except Exception as e:
        logger.error(f"Error in bulk add: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{cart_id}/items/{item_id}", response_model=CartItemResponse)
async def update_item_quantity(
    cart_id: str,
    item_id: str,
    request: CartItemUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update quantity of item in cart"""
    try:
        service = CartService(db)
        item = await service.update_item_quantity(cart_id, item_id, request.quantity)
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item {item_id} not found in cart {cart_id}"
            )
        
        return item.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{cart_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item(
    cart_id: str,
    item_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Remove item from cart"""
    try:
        service = CartService(db)
        success = await service.remove_item(cart_id, item_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item {item_id} not found in cart {cart_id}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==================== Validation ====================

@router.post("/{cart_id}/validate", response_model=CartValidationResult)
async def validate_cart(
    cart_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Validate cart (check prices and inventory)"""
    try:
        service = CartService(db)
        is_valid, invalid_items = await service.validate_cart(cart_id)
        
        message = "Cart is valid" if is_valid else f"Cart has {len(invalid_items)} invalid items"
        
        return {
            "cart_id": cart_id,
            "is_valid": is_valid,
            "invalid_items": invalid_items,
            "errors": [item["errors"] for item in invalid_items] if invalid_items else [],
            "message": message
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error validating cart: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==================== Checkout ====================

@router.post("/{cart_id}/checkout", response_model=CheckoutResponse)
async def checkout(
    cart_id: str,
    request: CheckoutRequest | None = None,
    db: AsyncSession = Depends(get_db)
):
    """Prepare checkout (validate and group by store)"""
    try:
        service = CartService(db)
        
        if request and request.cart_id and request.cart_id != cart_id:
            raise ValueError("Cart ID mismatch")
        
        checkout_data = await service.prepare_checkout(cart_id)
        
        return {
            "success": True,
            "message": f"Checkout prepared for {checkout_data['stores_count']} store(s)",
            "order_ids": None,  # Would be populated by Order Service
            "split_orders": checkout_data['stores_count'],
            "orders_count": checkout_data['stores_count']
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error during checkout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==================== Health Check ====================

@router.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "cart_service",
        "version": "1.0.0"
    }
