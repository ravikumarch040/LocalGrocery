from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, delete, and_
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple
import httpx
import logging

from app.models import Cart, CartItem
from app.config import settings

logger = logging.getLogger(__name__)


class CartService:
    """Business logic for shopping cart operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.http_client = None
    
    async def __aenter__(self):
        self.http_client = httpx.AsyncClient()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.http_client:
            await self.http_client.aclose()
    
    # ==================== Cart Operations ====================
    
    async def create_cart(self, customer_id: str) -> Cart:
        """Create a new cart for a customer"""
        logger.info(f"Creating cart for customer {customer_id}")
        
        # Check if customer already has active cart (without loading items for performance)
        now = datetime.utcnow()
        stmt = select(Cart).where(
            and_(
                Cart.customer_id == customer_id,
                (Cart.expires_at.is_(None)) | (Cart.expires_at > now)
            )
        ).order_by(Cart.created_at.desc())
        
        result = await self.db.execute(stmt)
        existing_cart = result.scalar_one_or_none()
        
        if existing_cart:
            logger.info(f"Customer {customer_id} already has active cart {existing_cart.id}")
            return existing_cart
        
        # Create new cart with explicit values to avoid async issues
        from uuid import uuid4
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=settings.CART_TTL_HOURS)
        
        cart = Cart(
            id=uuid4(),
            customer_id=customer_id,
            created_at=now,
            updated_at=now,
            expires_at=expires_at
        )
        self.db.add(cart)
        await self.db.commit()

        logger.info(f"Cart created: {cart.id}")

        # Avoid lazy-loading relationships during response serialization
        return {
            "id": str(cart.id),
            "customer_id": cart.customer_id,
            "items_count": 0,
            "total_items": 0,
            "created_at": cart.created_at,
            "updated_at": cart.updated_at,
        }
    
    async def get_cart(self, cart_id: str) -> Optional[Cart]:
        """Get cart by ID with all items"""
        stmt = select(Cart).where(Cart.id == cart_id).options(selectinload(Cart.items))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_active_cart(self, customer_id: str) -> Optional[Cart]:
        """Get customer's active cart"""
        now = datetime.utcnow()  # Call once before query construction
        stmt = select(Cart).where(
            and_(
                Cart.customer_id == customer_id,
                (Cart.expires_at.is_(None)) | (Cart.expires_at > now)
            )
        ).options(selectinload(Cart.items)).order_by(Cart.created_at.desc())
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def clear_cart(self, cart_id: str) -> bool:
        """Clear all items from cart"""
        logger.info(f"Clearing cart {cart_id}")
        
        # Delete all items
        stmt = delete(CartItem).where(CartItem.cart_id == cart_id)
        await self.db.execute(stmt)
        await self.db.commit()
        
        return True
    
    async def delete_cart(self, cart_id: str) -> bool:
        """Delete entire cart"""
        logger.info(f"Deleting cart {cart_id}")
        
        cart = await self.get_cart(cart_id)
        if not cart:
            return False
        
        await self.db.delete(cart)
        await self.db.commit()
        
        return True
    
    # ==================== Cart Item Operations ====================
    
    async def add_item(
        self,
        cart_id: str,
        product_id: str,
        store_id: str,
        quantity: int,
        unit_price: float,
        product_name: Optional[str] = None,
        product_image_url: Optional[str] = None
    ) -> CartItem:
        """Add item to cart or increment if exists"""
        logger.info(f"Adding item {product_id} to cart {cart_id}")
        
        cart = await self.get_cart(cart_id)
        if not cart:
            raise ValueError(f"Cart {cart_id} not found")
        
        # Check cart size limit
        if len(cart.items) >= settings.MAX_CART_ITEMS:
            raise ValueError(f"Cart has reached maximum items ({settings.MAX_CART_ITEMS})")
        
        # Check if item already exists
        existing_item = await self.get_cart_item_by_product(cart_id, product_id, store_id)
        
        if existing_item:
            # Update quantity
            existing_item.quantity += quantity
            existing_item.updated_at = datetime.utcnow()
            logger.info(f"Updated quantity to {existing_item.quantity}")
            # Keep cached details updated when provided
            if product_name:
                existing_item.product_name = product_name
            if product_image_url:
                existing_item.product_image_url = product_image_url
        else:
            # Create new item with explicit values
            from uuid import uuid4
            now = datetime.utcnow()
            item = CartItem(
                id=uuid4(),
                cart_id=cart_id,
                product_id=product_id,
                store_id=store_id,
                quantity=quantity,
                unit_price=unit_price,
                product_name=product_name,
                product_image_url=product_image_url,
                created_at=now,
                updated_at=now
            )
            self.db.add(item)
            existing_item = item
        
        cart.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(existing_item)
        
        return existing_item
    
    async def remove_item(self, cart_id: str, item_id: str) -> bool:
        """Remove item from cart"""
        logger.info(f"Removing item {item_id} from cart {cart_id}")
        
        item = await self.get_cart_item(item_id)
        if not item or str(item.cart_id) != cart_id:
            return False
        
        await self.db.delete(item)
        
        # Update cart
        cart = await self.get_cart(cart_id)
        if cart:
            cart.updated_at = datetime.utcnow()
        
        await self.db.commit()
        return True
    
    async def update_item_quantity(
        self,
        cart_id: str,
        item_id: str,
        quantity: int
    ) -> Optional[CartItem]:
        """Update cart item quantity"""
        logger.info(f"Updating item {item_id} quantity to {quantity}")
        
        item = await self.get_cart_item(item_id)
        if not item or str(item.cart_id) != cart_id:
            return None
        
        if quantity <= 0:
            await self.remove_item(cart_id, item_id)
            return None
        
        item.quantity = quantity
        item.updated_at = datetime.utcnow()
        
        # Update cart
        cart = await self.get_cart(cart_id)
        if cart:
            cart.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(item)
        
        return item
    
    async def get_cart_item(self, item_id: str) -> Optional[CartItem]:
        """Get specific cart item"""
        stmt = select(CartItem).where(CartItem.id == item_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_cart_item_by_product(
        self,
        cart_id: str,
        product_id: str,
        store_id: str
    ) -> Optional[CartItem]:
        """Get cart item by product and store"""
        stmt = select(CartItem).where(
            and_(
                CartItem.cart_id == cart_id,
                CartItem.product_id == product_id,
                CartItem.store_id == store_id
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    # ==================== Cart Validation ====================
    
    async def validate_cart(self, cart_id: str) -> Tuple[bool, List[Dict]]:
        """Validate all items in cart (price & inventory)"""
        logger.info(f"Validating cart {cart_id}")
        
        cart = await self.get_cart(cart_id)
        if not cart:
            raise ValueError(f"Cart {cart_id} not found")
        
        invalid_items = []
        
        for item in cart.items:
            errors = []
            
            # Validate with Catalog Service (price)
            price_valid = await self._validate_product_price(item.product_id, item.unit_price)
            if not price_valid:
                errors.append(f"Price changed for product {item.product_id}")
                item.is_price_valid = False
            else:
                item.is_price_valid = True
            
            # Validate with Inventory Service (stock)
            in_stock = await self._validate_inventory(item.product_id, item.store_id, item.quantity)
            if not in_stock:
                errors.append(f"Insufficient stock for {item.product_id}")
                item.is_in_stock = False
            else:
                item.is_in_stock = True
            
            if errors:
                item.validation_errors = errors
                invalid_items.append({
                    "item_id": str(item.id),
                    "product_id": item.product_id,
                    "errors": errors
                })
        
        await self.db.commit()
        
        is_valid = len(invalid_items) == 0
        logger.info(f"Cart validation result: {is_valid}, invalid items: {len(invalid_items)}")
        
        return is_valid, invalid_items
    
    async def _validate_product_price(self, product_id: str, unit_price: float) -> bool:
        """Check if product price hasn't changed"""
        try:
            if not self.http_client:
                self.http_client = httpx.AsyncClient()
            
            response = await self.http_client.get(
                f"{settings.CATALOG_SERVICE_URL}/v1/products/{product_id}",
                timeout=5.0
            )
            
            if response.status_code != 200:
                logger.warning(f"Could not validate price for product {product_id}")
                return True  # Allow if service unavailable
            
            data = response.json()
            current_price = data.get("data", {}).get("price", unit_price)
            
            # Allow small price variance (±5%)
            variance = abs(current_price - unit_price) / unit_price
            return variance <= 0.05
            
        except Exception as e:
            logger.error(f"Error validating price: {e}")
            return True  # Allow on error
    
    async def _validate_inventory(self, product_id: str, store_id: str, quantity: int) -> bool:
        """Check if product is in stock"""
        try:
            if not self.http_client:
                self.http_client = httpx.AsyncClient()
            
            response = await self.http_client.get(
                f"{settings.INVENTORY_SERVICE_URL}/v1/inventory/{store_id}/{product_id}",
                timeout=5.0
            )
            
            if response.status_code != 200:
                logger.warning(f"Could not check inventory for {product_id} in store {store_id}")
                return True  # Allow if service unavailable
            
            data = response.json()
            available_qty = data.get("data", {}).get("stock_qty", 0)
            
            return available_qty >= quantity
            
        except Exception as e:
            logger.error(f"Error validating inventory: {e}")
            return True  # Allow on error
    
    # ==================== Cart Summary ====================
    
    def calculate_cart_totals(self, cart: Cart) -> Dict:
        """Calculate total amount and item count"""
        total_amount = sum(item.unit_price * item.quantity for item in cart.items)
        total_items = sum(item.quantity for item in cart.items)
        
        return {
            "total_amount": round(total_amount, 2),
            "total_items": total_items,
            "items_count": len(cart.items)
        }
    
    async def group_items_by_store(self, cart: Cart) -> Dict[str, List[CartItem]]:
        """Group cart items by store (for order splitting)"""
        grouped = {}
        for item in cart.items:
            if item.store_id not in grouped:
                grouped[item.store_id] = []
            grouped[item.store_id].append(item)
        
        return grouped
    
    # ==================== Checkout ====================
    
    async def prepare_checkout(self, cart_id: str) -> Dict:
        """Prepare cart for checkout (validate and group by store)"""
        logger.info(f"Preparing checkout for cart {cart_id}")
        
        cart = await self.get_cart(cart_id)
        if not cart or len(cart.items) == 0:
            raise ValueError("Cart is empty")
        
        # Validate cart
        is_valid, invalid_items = await self.validate_cart(cart_id)
        
        if not is_valid:
            raise ValueError(f"Cart validation failed: {invalid_items}")
        
        # Group by store
        grouped = await self.group_items_by_store(cart)
        
        totals = self.calculate_cart_totals(cart)
        
        checkout_data = {
            "cart_id": str(cart.id),
            "customer_id": cart.customer_id,
            "stores_count": len(grouped),
            "total_amount": totals["total_amount"],
            "total_items": totals["total_items"],
            "grouped_items": {
                store_id: [
                    {
                        "item_id": str(item.id),
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price
                    }
                    for item in items
                ]
                for store_id, items in grouped.items()
            }
        }
        
        logger.info(f"Checkout prepared: {len(grouped)} stores")
        return checkout_data
