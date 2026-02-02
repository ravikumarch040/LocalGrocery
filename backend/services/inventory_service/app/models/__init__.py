from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Enum, ForeignKey, UniqueConstraint, Index, func, JSON
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone
import uuid
import enum

Base = declarative_base()


class StockStatus(str, enum.Enum):
    IN_STOCK = "IN_STOCK"
    LOW_STOCK = "LOW_STOCK"
    OUT_OF_STOCK = "OUT_OF_STOCK"


class ReservationStatus(str, enum.Enum):
    RESERVED = "RESERVED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class InventoryLog(str, enum.Enum):
    STOCK_ADDED = "STOCK_ADDED"
    STOCK_REMOVED = "STOCK_REMOVED"
    STOCK_ADJUSTED = "STOCK_ADJUSTED"
    STOCK_RESERVED = "STOCK_RESERVED"
    STOCK_UNRESERVED = "STOCK_UNRESERVED"
    STOCK_CONFIRMED = "STOCK_CONFIRMED"
    LOW_STOCK_ALERT = "LOW_STOCK_ALERT"
    OUT_OF_STOCK_ALERT = "OUT_OF_STOCK_ALERT"


class ProductInventory(Base):
    """
    Real-time stock tracking for products in stores
    Primary: store_id + product_id
    Cache: Redis key "inventory:{store_id}:{product_id}"
    """
    __tablename__ = "product_inventory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    store_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Stock quantities
    stock_qty = Column(Integer, nullable=False, default=0)
    reserved_qty = Column(Integer, nullable=False, default=0)
    available_qty = Column(Integer, nullable=False, default=0)
    
    # Pricing
    cost_price = Column(Float, nullable=False, default=0.0)
    selling_price = Column(Float, nullable=False, default=0.0)
    
    # Status & thresholds
    status = Column(Enum(StockStatus), nullable=False, default=StockStatus.IN_STOCK)
    reorder_level = Column(Integer, nullable=False, default=10)
    reorder_qty = Column(Integer, nullable=False, default=50)
    
    # Supplier & batch info
    supplier_id = Column(UUID(as_uuid=True), nullable=True)
    batch_number = Column(String(100), nullable=True)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    product_metadata = Column(JSONB, nullable=True)  # SKU, barcode, HSN, MRP
    last_stock_check = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        UniqueConstraint('store_id', 'product_id', name='uq_store_product'),
        Index('idx_product_inventory_store_id', 'store_id'),
        Index('idx_product_inventory_product_id', 'product_id'),
        Index('idx_product_inventory_status', 'status'),
        Index('idx_product_inventory_stock_qty', 'stock_qty'),
    )


class InventoryReservation(Base):
    """
    Track inventory reservations during checkout
    Expires after RESERVATION_VALIDITY_MINUTES (default 15 mins)
    Links to Order via order_id
    """
    __tablename__ = "inventory_reservations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    customer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Reservation items (JSON)
    # Format: [{"store_id": "...", "product_id": "...", "qty": 2, "inventory_id": "..."}]
    items = Column(JSONB, nullable=False)
    
    # Status tracking
    status = Column(Enum(ReservationStatus), nullable=False, default=ReservationStatus.RESERVED)
    reserved_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    reason = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        Index('idx_reservation_order_id', 'order_id'),
        Index('idx_reservation_customer_id', 'customer_id'),
        Index('idx_reservation_status', 'status'),
        Index('idx_reservation_expires_at', 'expires_at'),
    )


class StockAuditLog(Base):
    """
    Immutable audit trail for all inventory operations
    For compliance, traceability, and debugging
    """
    __tablename__ = "stock_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inventory_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # What happened
    event_type = Column(Enum(InventoryLog), nullable=False)
    old_qty = Column(Integer, nullable=False)
    new_qty = Column(Integer, nullable=False)
    qty_changed = Column(Integer, nullable=False)  # old_qty - new_qty
    
    # Context
    order_id = Column(UUID(as_uuid=True), nullable=True)
    user_id = Column(UUID(as_uuid=True), nullable=True)  # Retailer who adjusted
    source = Column(String(50), nullable=False)  # "ORDER", "MANUAL_ADJUSTMENT", "RETURN", "DAMAGE"
    
    # Additional info
    notes = Column(Text, nullable=True)
    extra_data = Column(JSONB, nullable=True)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        Index('idx_audit_log_inventory_id', 'inventory_id'),
        Index('idx_audit_log_event_type', 'event_type'),
        Index('idx_audit_log_order_id', 'order_id'),
        Index('idx_audit_log_created_at', 'created_at'),
    )
