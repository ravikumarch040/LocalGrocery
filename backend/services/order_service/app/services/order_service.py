"""Order service - business logic for order operations"""
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import selectinload
from decimal import Decimal
from uuid import UUID
from datetime import datetime
import uuid

from app.models import Order, OrderItem, OrderStatus, PaymentStatus
from app.api.v1.schemas.orders import OrderCreate, OrderUpdate


class OrderService:
    """Order management service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_order(self, order_data: OrderCreate) -> Order:
        """Create a new order with items"""
        # Generate unique order number (e.g., ORD-20260118-001)
        today = datetime.utcnow().strftime("%Y%m%d")
        count = await self._get_order_count_today()
        order_number = f"ORD-{today}-{str(count + 1).zfill(3)}"
        
        # Calculate totals
        subtotal = Decimal(0)
        for item in order_data.items:
            item_total = item.quantity * item.unit_price
            subtotal += item_total
        
        # Create order (no tax/delivery fee for MVP - can be extended)
        tax = Decimal(0)
        delivery_fee = Decimal(0)
        discount = Decimal(0)
        total_amount = subtotal + tax + delivery_fee - discount
        
        order = Order(
            customer_id=order_data.customer_id,
            store_id=order_data.store_id,
            order_number=order_number,
            status=OrderStatus.PLACED,
            payment_status=PaymentStatus.PENDING,
            subtotal=subtotal,
            tax=tax,
            delivery_fee=delivery_fee,
            discount=discount,
            total_amount=total_amount,
            delivery_address=order_data.delivery_address,
            payment_method=order_data.payment_method,
            notes=order_data.notes,
            idempotency_key=str(uuid.uuid4())  # For webhook idempotency
        )
        
        # Add items
        for item in order_data.items:
            order_item = OrderItem(
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.quantity * item.unit_price,
                variant_data=item.variant_data or {}
            )
            order.items.append(order_item)
        
        self.db.add(order)
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(order)
        
        return order
    
    async def get_order(self, order_id: UUID) -> Optional[Order]:
        """Get order by ID with items"""
        result = await self.db.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.id == order_id)
        )
        return result.scalar_one_or_none()
    
    async def get_order_by_number(self, order_number: str) -> Optional[Order]:
        """Get order by order number"""
        result = await self.db.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.order_number == order_number)
        )
        return result.scalar_one_or_none()
    
    async def update_order_status(
        self,
        order_id: UUID,
        new_status: OrderStatus
    ) -> Optional[Order]:
        """Update order status"""
        order = await self.get_order(order_id)
        if not order:
            return None
        
        # Validate status transition
        valid_transitions = {
            OrderStatus.PLACED: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
            OrderStatus.CONFIRMED: [OrderStatus.PACKED, OrderStatus.CANCELLED],
            OrderStatus.PACKED: [OrderStatus.OUT_FOR_DELIVERY],
            OrderStatus.OUT_FOR_DELIVERY: [OrderStatus.DELIVERED],
            OrderStatus.DELIVERED: [],
            OrderStatus.CANCELLED: [],
        }
        
        if new_status not in valid_transitions.get(order.status, []):
            raise ValueError(
                f"Cannot transition from {order.status} to {new_status}"
            )
        
        order.status = new_status
        
        # Update timestamps
        if new_status == OrderStatus.CONFIRMED:
            order.confirmed_at = datetime.utcnow()
        elif new_status == OrderStatus.DELIVERED:
            order.delivered_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(order)
        
        return order
    
    async def update_payment_status(
        self,
        order_id: UUID,
        payment_status: PaymentStatus,
        payment_gateway: str,
        payment_gateway_order_id: str
    ) -> Optional[Order]:
        """Update order payment status"""
        order = await self.get_order(order_id)
        if not order:
            return None
        
        order.payment_status = payment_status
        order.payment_gateway = payment_gateway
        order.payment_gateway_order_id = payment_gateway_order_id
        
        await self.db.commit()
        await self.db.refresh(order)
        
        return order
    
    async def list_orders(
        self,
        customer_id: Optional[UUID] = None,
        store_id: Optional[UUID] = None,
        status: Optional[OrderStatus] = None,
        payment_status: Optional[PaymentStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[Order], int]:
        """List orders with filters and pagination"""
        query = select(Order).options(selectinload(Order.items))
        
        conditions = []
        if customer_id:
            conditions.append(Order.customer_id == customer_id)
        if store_id:
            conditions.append(Order.store_id == store_id)
        if status:
            conditions.append(Order.status == status)
        if payment_status:
            conditions.append(Order.payment_status == payment_status)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Get total count
        count_query = select(func.count()).select_from(Order)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(desc(Order.created_at))
        
        result = await self.db.execute(query)
        orders = result.scalars().unique().all()
        
        return orders, total
    
    async def cancel_order(self, order_id: UUID) -> Optional[Order]:
        """Cancel an order"""
        order = await self.get_order(order_id)
        if not order:
            return None
        
        # Only allow cancelling if order is in certain states
        if order.status not in [OrderStatus.PLACED, OrderStatus.CONFIRMED]:
            raise ValueError(f"Cannot cancel order with status {order.status}")
        
        order.status = OrderStatus.CANCELLED
        await self.db.commit()
        await self.db.refresh(order)
        
        return order
    
    async def _get_order_count_today(self) -> int:
        """Get count of orders created today"""
        today = datetime.utcnow().date()
        result = await self.db.execute(
            select(func.count()).select_from(Order)
            .where(func.date(Order.created_at) == today)
        )
        return result.scalar() or 0
