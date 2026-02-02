from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import (
    CreateInventoryRequest,
    UpdateInventoryRequest,
    AdjustStockRequest,
    ReserveInventoryRequest,
    ConfirmReservationRequest,
    CancelReservationRequest,
    CheckAvailabilityRequest,
    InventoryResponse,
    ReservationResponse,
    AvailabilityCheckResponse,
    StockAuditLogResponse,
    StandardResponse,
)
from app.services.inventory_service import InventoryService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/v1/inventory", status_code=status.HTTP_201_CREATED)
async def create_inventory(
    req: CreateInventoryRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create new product inventory"""
    print(f"[DEBUG] CREATE ENDPOINT CALLED")
    try:
        service = InventoryService(db)
        inventory = await service.create_inventory(
            store_id=req.store_id,
            product_id=req.product_id,
            stock_qty=req.stock_qty,
            cost_price=req.cost_price,
            selling_price=req.selling_price,
            reorder_level=req.reorder_level,
            reorder_qty=req.reorder_qty,
            supplier_id=req.supplier_id,
            batch_number=req.batch_number,
            expiry_date=req.expiry_date,
            product_metadata=req.product_metadata,
        )
        result = {
            "id": str(inventory.id),
            "store_id": str(inventory.store_id),
            "product_id": str(inventory.product_id),
            "stock_qty": inventory.stock_qty,
            "available_qty": inventory.available_qty,
            "reserved_qty": inventory.reserved_qty,
            "status": inventory.status.value if hasattr(inventory.status, 'value') else str(inventory.status),
            "cost_price": inventory.cost_price,
            "selling_price": inventory.selling_price,
        }
        print(f"[DEBUG] Returning: {result}")
        return result
    except ValueError as e:
        print(f"[ValueError] {str(e)}")
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {str(e)[:200]}")
        raise HTTPException(
            status_code=500,
            detail=f"Error: {type(e).__name__}: {str(e)[:200]}",
        )


@router.get("/v1/inventory/{store_id}/{product_id}")
async def get_inventory(
    store_id: str,
    product_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get inventory by store and product"""
    try:
        service = InventoryService(db)
        inventory = await service.get_inventory(store_id, product_id)
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory not found",
            )
        return {
            "id": str(inventory.id),
            "store_id": str(inventory.store_id),
            "product_id": str(inventory.product_id),
            "stock_qty": inventory.stock_qty,
            "reserved_qty": inventory.reserved_qty,
            "available_qty": inventory.available_qty,
            "status": inventory.status.value if hasattr(inventory.status, 'value') else str(inventory.status),
            "cost_price": inventory.cost_price,
            "selling_price": inventory.selling_price,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching inventory: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch inventory",
        )


@router.post("/v1/inventory/check-availability")
async def check_availability(
    req: CheckAvailabilityRequest,
    db: AsyncSession = Depends(get_db),
):
    """Check if items are available for cart validation"""
    try:
        service = InventoryService(db)
        result = await service.check_availability(req.items)
        # Convert result to dict format expected by API
        if isinstance(result, dict):
            return result
        # If it's an object, serialize it
        return {
            "all_available": getattr(result, 'all_available', False),
            "items": getattr(result, 'items', []),
        }
    except Exception as e:
        logger.error(f"Error checking availability: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check availability: {str(e)[:200]}",
        )


@router.post("/v1/inventory/{store_id}/{product_id}/adjust")
async def adjust_stock(
    store_id: str,
    product_id: str,
    req: AdjustStockRequest,
    db: AsyncSession = Depends(get_db),
):
    """Adjust inventory (manual, returns, damage, etc.)"""
    try:
        service = InventoryService(db)
        inventory = await service.adjust_stock(
            store_id=store_id,
            product_id=product_id,
            qty_change=req.qty_change,
            source=req.source,
            user_id=req.user_id,
            notes=req.notes,
            metadata=req.metadata,
        )
        return {
            "id": str(inventory.id),
            "store_id": str(inventory.store_id),
            "product_id": str(inventory.product_id),
            "stock_qty": inventory.stock_qty,
            "available_qty": inventory.available_qty,
            "reserved_qty": inventory.reserved_qty,
            "status": inventory.status.value if hasattr(inventory.status, 'value') else str(inventory.status),
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error adjusting stock: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to adjust stock",
        )


@router.post("/v1/reservations", status_code=status.HTTP_201_CREATED)
async def reserve_inventory(
    req: ReserveInventoryRequest,
    db: AsyncSession = Depends(get_db),
):
    """Reserve inventory for an order (during checkout)"""
    try:
        service = InventoryService(db)
        reservation = await service.reserve_inventory(
            order_id=req.order_id,
            customer_id=req.customer_id,
            items=req.items,
        )
        return {
            "reservation_id": str(reservation.id),
            "id": str(reservation.id),
            "order_id": str(reservation.order_id),
            "customer_id": str(reservation.customer_id),
            "status": reservation.status.value if hasattr(reservation.status, 'value') else str(reservation.status),
            "items": reservation.items,  # Include items array
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        logger.error(f"Error reserving inventory: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reserve inventory",
        )


@router.post("/v1/reservations/{order_id}/confirm")
async def confirm_reservation(
    order_id: str,
    req: ConfirmReservationRequest,
    db: AsyncSession = Depends(get_db),
):
    """Confirm reservation after payment success"""
    try:
        service = InventoryService(db)
        reservation = await service.confirm_reservation(order_id, req.reason)
        return {
            "id": str(reservation.id),
            "order_id": str(reservation.order_id),
            "customer_id": str(reservation.customer_id),
            "status": reservation.status.value if hasattr(reservation.status, 'value') else str(reservation.status),
            "items": reservation.items,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error confirming reservation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to confirm reservation",
        )


@router.post("/v1/reservations/{order_id}/cancel")
async def cancel_reservation(
    order_id: str,
    req: CancelReservationRequest,
    db: AsyncSession = Depends(get_db),
):
    """Cancel reservation and restore stock"""
    try:
        service = InventoryService(db)
        reservation = await service.cancel_reservation(order_id, req.reason)
        return {
            "id": str(reservation.id),
            "order_id": str(reservation.order_id),
            "customer_id": str(reservation.customer_id),
            "status": reservation.status.value if hasattr(reservation.status, 'value') else str(reservation.status),
            "items": reservation.items,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error cancelling reservation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel reservation",
        )


@router.get("/v1/audit-logs/{inventory_id}")
async def get_audit_logs(
    inventory_id: str,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """Get stock audit trail for inventory"""
    try:
        service = InventoryService(db)
        logs = await service.get_audit_log(inventory_id, limit, offset)
        # Convert ORM objects to dicts
        logs_data = []
        for log in logs:
            logs_data.append({
                "id": str(log.id),
                "inventory_id": str(log.inventory_id),
                "event_type": str(log.event_type.value if hasattr(log.event_type, 'value') else log.event_type),
                "old_qty": log.old_qty,
                "new_qty": log.new_qty,
                "qty_changed": log.qty_changed,
                "created_at": log.created_at.isoformat(),
                "user_id": str(log.user_id) if log.user_id else None,
                "order_id": str(log.order_id) if log.order_id else None,
                "source": log.source,
                "notes": log.notes,
            })
        return {
            "success": True,
            "count": len(logs),
            "data": logs_data,
        }
    except Exception as e:
        logger.error(f"Error fetching audit logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch audit logs",
        )
