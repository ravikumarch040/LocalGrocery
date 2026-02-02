"""Order endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.services.order_service import OrderService
from app.models import OrderStatus, PaymentStatus
from app.api.v1.schemas.orders import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderListResponse,
    StandardResponse
)

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: OrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new order"""
    try:
        service = OrderService(db)
        new_order = await service.create_order(order)
        return new_order
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create order: {str(e)}"
        )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get order by ID"""
    service = OrderService(db)
    order = await service.get_order(order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order


@router.get("/number/{order_number}", response_model=OrderResponse)
async def get_order_by_number(
    order_number: str,
    db: AsyncSession = Depends(get_db)
):
    """Get order by order number"""
    service = OrderService(db)
    order = await service.get_order_by_number(order_number)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order


@router.get("/", response_model=OrderListResponse)
async def list_orders(
    customer_id: Optional[UUID] = Query(None),
    store_id: Optional[UUID] = Query(None),
    status: Optional[OrderStatus] = Query(None),
    payment_status: Optional[PaymentStatus] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List orders with filters"""
    service = OrderService(db)
    orders, total = await service.list_orders(
        customer_id=customer_id,
        store_id=store_id,
        status=status,
        payment_status=payment_status,
        page=page,
        page_size=page_size
    )
    
    return OrderListResponse(
        orders=orders,
        total=total,
        page=page,
        page_size=page_size
    )


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order_status(
    order_id: UUID,
    order_update: OrderUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update order status"""
    service = OrderService(db)
    
    try:
        if order_update.status:
            order = await service.update_order_status(order_id, order_update.status)
        else:
            order = await service.get_order(order_id)
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        return order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{order_id}", response_model=StandardResponse)
async def cancel_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Cancel an order"""
    service = OrderService(db)
    
    try:
        order = await service.cancel_order(order_id)
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        return StandardResponse(
            success=True,
            message="Order cancelled successfully",
            data={"order_id": str(order.id)}
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
