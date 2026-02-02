import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, func
from sqlalchemy.orm import selectinload
from uuid import UUID
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
import httpx
import json

from app.models import (
    ProductInventory,
    InventoryReservation,
    StockAuditLog,
    StockStatus,
    ReservationStatus,
    InventoryLog,
)
from app.cache import (
    get_inventory_cache,
    set_inventory_cache,
    invalidate_inventory_cache,
    invalidate_store_cache,
    set_reservation_cache,
    invalidate_reservation_cache,
)
from app.config import settings

logger = logging.getLogger(__name__)


class InventoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_inventory(
        self,
        store_id: str,
        product_id: str,
        stock_qty: int,
        cost_price: float,
        selling_price: float,
        reorder_level: int = 10,
        reorder_qty: int = 50,
        supplier_id: Optional[str] = None,
        batch_number: Optional[str] = None,
        expiry_date: Optional[datetime] = None,
        product_metadata: Optional[Dict] = None,
    ) -> ProductInventory:
        """Create new product inventory record"""
        try:
            # Check if already exists
            stmt = select(ProductInventory).where(
                and_(
                    ProductInventory.store_id == store_id,
                    ProductInventory.product_id == product_id,
                )
            )
            existing = await self.db.scalar(stmt)
            if existing:
                raise ValueError(f"Inventory already exists for this store and product")

            # Create inventory
            status = StockStatus.IN_STOCK if stock_qty > 0 else StockStatus.OUT_OF_STOCK
            inventory = ProductInventory(
                store_id=store_id,
                product_id=product_id,
                stock_qty=stock_qty,
                available_qty=stock_qty,
                reserved_qty=0,
                cost_price=cost_price,
                selling_price=selling_price,
                status=status,
                reorder_level=reorder_level,
                reorder_qty=reorder_qty,
                supplier_id=supplier_id,
                batch_number=batch_number,
                expiry_date=expiry_date,
                product_metadata=product_metadata,
                last_stock_check=datetime.now(timezone.utc),
            )
            self.db.add(inventory)
            await self.db.flush()

            # Log the creation
            await self._log_stock_event(
                inventory.id,
                InventoryLog.STOCK_ADDED,
                0,
                stock_qty,
                source="INVENTORY_CREATE",
            )

            await self.db.commit()
            logger.info(f"Created inventory: {inventory.id} (store={store_id}, product={product_id})")
            return inventory

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating inventory: {str(e)}")
            raise

    async def get_inventory(self, store_id: str, product_id: str) -> Optional[ProductInventory]:
        """Get inventory with cache check"""
        # Try cache first
        cached = await get_inventory_cache(store_id, product_id)
        if cached:
            logger.info(f"Cache hit: inventory:{store_id}:{product_id}")
            return cached

        # Query database
        stmt = select(ProductInventory).where(
            and_(
                ProductInventory.store_id == store_id,
                ProductInventory.product_id == product_id,
            )
        )
        inventory = await self.db.scalar(stmt)

        if inventory:
            # Cache the result
            inventory_dict = {
                "id": str(inventory.id),
                "store_id": str(inventory.store_id),
                "product_id": str(inventory.product_id),
                "stock_qty": inventory.stock_qty,
                "reserved_qty": inventory.reserved_qty,
                "available_qty": inventory.available_qty,
                "cost_price": inventory.cost_price,
                "selling_price": inventory.selling_price,
                "status": inventory.status.value,
            }
            await set_inventory_cache(store_id, product_id, inventory_dict)

        return inventory

    async def check_availability(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check if items are available (for cart validation)"""
        items_status = []
        unavailable_items = []

        for item in items:
            store_id = item.get("store_id")
            product_id = item.get("product_id")
            qty = item.get("qty") or item.get("quantity", 0)  # Support both qty and quantity

            inventory = await self.get_inventory(store_id, product_id)

            # Handle both ORM objects and dicts from cache
            available_qty = 0
            if inventory:
                if isinstance(inventory, dict):
                    available_qty = inventory.get("available_qty", 0)
                else:
                    available_qty = inventory.available_qty

            if not inventory or available_qty < qty:
                unavailable_items.append(product_id)
                status = {
                    "product_id": product_id,
                    "requested_qty": qty,
                    "available_qty": available_qty,
                    "in_stock": False,
                }
            else:
                status = {
                    "product_id": product_id,
                    "requested_qty": qty,
                    "available_qty": available_qty,
                    "in_stock": True,
                }

            items_status.append(status)

        return {
            "all_available": len(unavailable_items) == 0,
            "items": items_status,
            "items_status": items_status,
        }

    async def reserve_inventory(
        self,
        order_id: str,
        customer_id: str,
        items: List[Dict[str, Any]],
    ) -> InventoryReservation:
        """
        Reserve inventory for an order (during checkout).
        Locks stock with SELECT ... FOR UPDATE to prevent race conditions.
        Expires after RESERVATION_VALIDITY_MINUTES.
        """
        try:
            # Check availability and lock rows
            reserved_items = []
            for item in items:
                store_id = item.get("store_id")
                product_id = item.get("product_id")
                qty = item.get("qty", 0)

                # Lock row for update
                stmt = select(ProductInventory).where(
                    and_(
                        ProductInventory.store_id == store_id,
                        ProductInventory.product_id == product_id,
                    )
                ).with_for_update()

                inventory = await self.db.scalar(stmt)

                if not inventory or inventory.available_qty < qty:
                    raise ValueError(
                        f"Insufficient stock: {product_id} "
                        f"(requested={qty}, available={inventory.available_qty if inventory else 0})"
                    )

                # Deduct from available
                inventory.available_qty -= qty
                inventory.reserved_qty += qty

                reserved_items.append({
                    "store_id": store_id,
                    "product_id": product_id,
                    "qty": qty,
                    "inventory_id": str(inventory.id),
                })

                # Log reservation
                await self._log_stock_event(
                    inventory.id,
                    InventoryLog.STOCK_RESERVED,
                    inventory.stock_qty,
                    inventory.stock_qty - qty,
                    order_id=order_id,
                    source="ORDER_CHECKOUT",
                )

            # Create reservation record
            expires_at = datetime.now(timezone.utc) + timedelta(
                minutes=settings.RESERVATION_VALIDITY_MINUTES
            )
            reservation = InventoryReservation(
                order_id=order_id,
                customer_id=customer_id,
                items=reserved_items,
                status=ReservationStatus.RESERVED,
                expires_at=expires_at,
            )
            self.db.add(reservation)
            await self.db.flush()

            # Cache reservation for quick expiry check
            await set_reservation_cache(
                order_id,
                {
                    "id": str(reservation.id),
                    "status": "RESERVED",
                    "expires_at": expires_at.isoformat(),
                },
            )

            await self.db.commit()
            logger.info(f"Reserved inventory: order={order_id}, items={len(reserved_items)}")
            return reservation

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error reserving inventory: {str(e)}")
            raise

    async def confirm_reservation(
        self,
        order_id: str,
        reason: Optional[str] = None,
    ) -> InventoryReservation:
        """Confirm reservation (after payment success)"""
        try:
            stmt = select(InventoryReservation).where(
                InventoryReservation.order_id == order_id
            )
            reservation = await self.db.scalar(stmt)

            if not reservation:
                raise ValueError(f"Reservation not found for order: {order_id}")

            if reservation.status != ReservationStatus.RESERVED:
                raise ValueError(f"Cannot confirm reservation with status: {reservation.status}")

            # Update to CONFIRMED
            reservation.status = ReservationStatus.CONFIRMED
            reservation.confirmed_at = datetime.now(timezone.utc)

            # Log each confirmed item
            for item in reservation.items:
                stmt = select(ProductInventory).where(
                    ProductInventory.id == item.get("inventory_id")
                )
                inventory = await self.db.scalar(stmt)
                if inventory:
                    await self._log_stock_event(
                        inventory.id,
                        InventoryLog.STOCK_CONFIRMED,
                        inventory.stock_qty,
                        inventory.stock_qty,
                        order_id=order_id,
                        source="ORDER_PAYMENT_SUCCESS",
                    )

            await self.db.commit()
            logger.info(f"Confirmed reservation: {order_id}")

            # Invalidate cache
            await invalidate_reservation_cache(order_id)

            return reservation

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error confirming reservation: {str(e)}")
            raise

    async def cancel_reservation(
        self,
        order_id: str,
        reason: str = "User cancelled",
    ) -> InventoryReservation:
        """Cancel reservation and restore stock"""
        try:
            stmt = select(InventoryReservation).where(
                InventoryReservation.order_id == order_id
            )
            reservation = await self.db.scalar(stmt)

            if not reservation:
                raise ValueError(f"Reservation not found for order: {order_id}")

            # Only cancel if still reserved or confirmed
            if reservation.status not in [ReservationStatus.RESERVED, ReservationStatus.CONFIRMED]:
                raise ValueError(f"Cannot cancel reservation with status: {reservation.status}")

            # Restore stock from each reserved item
            for item in reservation.items:
                inventory_id = item.get("inventory_id")
                qty = item.get("qty", 0)

                stmt = select(ProductInventory).where(
                    ProductInventory.id == inventory_id
                ).with_for_update()

                inventory = await self.db.scalar(stmt)
                if inventory:
                    inventory.available_qty += qty
                    inventory.reserved_qty -= qty

                    await self._log_stock_event(
                        inventory.id,
                        InventoryLog.STOCK_UNRESERVED,
                        inventory.stock_qty - qty,
                        inventory.stock_qty,
                        source="RESERVATION_CANCELLED",
                    )

            # Update reservation
            reservation.status = ReservationStatus.CANCELLED
            reservation.cancelled_at = datetime.now(timezone.utc)
            reservation.reason = reason

            await self.db.commit()
            logger.info(f"Cancelled reservation: {order_id}")

            # Invalidate caches
            await invalidate_reservation_cache(order_id)
            for item in reservation.items:
                await invalidate_inventory_cache(item.get("store_id"), item.get("product_id"))

            return reservation

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error cancelling reservation: {str(e)}")
            raise

    async def adjust_stock(
        self,
        store_id: str,
        product_id: str,
        qty_change: int,
        source: str = "MANUAL_ADJUSTMENT",
        user_id: Optional[str] = None,
        notes: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> ProductInventory:
        """
        Adjust inventory (manual stock count, returns, damage, etc.)
        qty_change > 0 = add stock
        qty_change < 0 = remove stock
        """
        try:
            stmt = select(ProductInventory).where(
                and_(
                    ProductInventory.store_id == store_id,
                    ProductInventory.product_id == product_id,
                )
            ).with_for_update()

            inventory = await self.db.scalar(stmt)
            if not inventory:
                raise ValueError(f"Inventory not found: {product_id}")

            old_qty = inventory.stock_qty
            new_qty = old_qty + qty_change

            if new_qty < 0:
                raise ValueError(f"Insufficient stock for reduction: {product_id}")

            # Update stock
            inventory.stock_qty = new_qty
            inventory.available_qty = new_qty - inventory.reserved_qty
            inventory.last_stock_check = datetime.now(timezone.utc)

            # Update status
            if new_qty == 0:
                inventory.status = StockStatus.OUT_OF_STOCK
            elif new_qty < inventory.reorder_level:
                inventory.status = StockStatus.LOW_STOCK
            else:
                inventory.status = StockStatus.IN_STOCK

            # Log adjustment
            event_type = (
                InventoryLog.STOCK_ADDED if qty_change > 0 else InventoryLog.STOCK_REMOVED
                if qty_change < 0 else InventoryLog.STOCK_ADJUSTED
            )

            await self._log_stock_event(
                inventory.id,
                event_type,
                old_qty,
                new_qty,
                user_id=user_id,
                source=source,
                notes=notes,
                metadata=metadata,
            )

            await self.db.commit()
            logger.info(f"Adjusted stock: {product_id} (old={old_qty}, new={new_qty}, change={qty_change})")

            # Invalidate cache
            await invalidate_inventory_cache(store_id, product_id)

            return inventory

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error adjusting stock: {str(e)}")
            raise

    async def cleanup_expired_reservations(self):
        """Background task: Cancel reservations past expiry time"""
        try:
            now = datetime.now(timezone.utc)
            stmt = select(InventoryReservation).where(
                and_(
                    InventoryReservation.status == ReservationStatus.RESERVED,
                    InventoryReservation.expires_at <= now,
                )
            )
            expired = await self.db.scalars(stmt)
            expired_list = list(expired)

            for reservation in expired_list:
                await self.cancel_reservation(
                    reservation.order_id,
                    reason="Reservation expired",
                )

            if expired_list:
                logger.info(f"Cleaned up {len(expired_list)} expired reservations")

        except Exception as e:
            logger.error(f"Error cleaning up expired reservations: {str(e)}")

    async def get_audit_log(
        self,
        inventory_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[StockAuditLog]:
        """Get stock audit trail"""
        stmt = select(StockAuditLog)
        if inventory_id:
            stmt = stmt.where(StockAuditLog.inventory_id == inventory_id)
        stmt = stmt.order_by(StockAuditLog.created_at.desc()).limit(limit).offset(offset)

        logs = await self.db.scalars(stmt)
        return list(logs)

    async def _log_stock_event(
        self,
        inventory_id,
        event_type: InventoryLog,
        old_qty: int,
        new_qty: int,
        order_id: Optional[str] = None,
        user_id: Optional[str] = None,
        source: str = "SYSTEM",
        notes: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        """Internal: Log to audit table"""
        log = StockAuditLog(
            inventory_id=inventory_id,
            event_type=event_type,
            old_qty=old_qty,
            new_qty=new_qty,
            qty_changed=old_qty - new_qty,
            order_id=order_id,
            user_id=user_id,
            source=source,
            notes=notes,
            metadata=metadata,
        )
        self.db.add(log)
