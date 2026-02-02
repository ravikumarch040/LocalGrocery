"""Payment Service - Business logic for payment processing"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models import Payment, PaymentLog, PaymentStatus, PaymentGateway, PaymentMethod
from app.api.v1.schemas.payments import (
    PaymentInitiateRequest, 
    RefundRequest,
    PaymentGatewayEnum,
    PaymentMethodEnum
)
from app.config import settings
from typing import Optional, List, Dict, Any
from datetime import datetime, UTC
import uuid
import hashlib
import hmac
import httpx
import logging

logger = logging.getLogger(__name__)


class PaymentService:
    """Service for payment operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def initiate_payment(
        self,
        request: PaymentInitiateRequest,
    ) -> Dict[str, Any]:
        """
        Initiate a payment with the selected gateway
        
        Returns payment details including gateway order ID and payment link
        """
        # Generate idempotency key
        idempotency_key = f"{request.order_id}-{request.customer_id}-{datetime.now(UTC).timestamp()}"
        
        # Check if payment already exists for this order
        existing_payment = await self.get_payment_by_order(request.order_id)
        if existing_payment and existing_payment.status not in [PaymentStatus.FAILED, PaymentStatus.CANCELLED]:
            logger.warning(f"Payment already exists for order {request.order_id}")
            return await self._format_payment_response(existing_payment)
        
        # Create payment record
        payment = Payment(
            id=uuid.uuid4(),
            order_id=request.order_id,
            customer_id=request.customer_id,
            amount=request.amount,
            currency=settings.DEFAULT_CURRENCY,
            payment_method=PaymentMethod(request.payment_method.value),
            payment_gateway=PaymentGateway(request.payment_gateway.value),
            status=PaymentStatus.PENDING,
            customer_email=request.customer_email,
            customer_phone=request.customer_phone,
            description=request.description or f"Payment for order {request.order_id}",
            idempotency_key=idempotency_key,
        )
        
        # Handle COD separately
        if request.payment_method == PaymentMethodEnum.COD:
            payment.payment_gateway = PaymentGateway.MANUAL
            payment.gateway_order_id = f"COD-{uuid.uuid4()}"
            payment.status = PaymentStatus.PENDING  # Will be marked SUCCESS on delivery
            
            self.db.add(payment)
            await self.db.flush()
            
            await self._log_payment_event(
                payment.id,
                "PAYMENT_CREATED",
                None,
                PaymentStatus.PENDING.value,
                {"payment_method": "COD"}
            )
            
            return await self._format_payment_response(payment)
        
        # Integrate with payment gateway
        if request.payment_gateway == PaymentGatewayEnum.RAZORPAY:
            gateway_data = await self._create_razorpay_order(payment)
        elif request.payment_gateway == PaymentGatewayEnum.CASHFREE:
            gateway_data = await self._create_cashfree_order(payment)
        else:
            raise ValueError(f"Unsupported payment gateway: {request.payment_gateway}")
        
        # Update payment with gateway details
        payment.gateway_order_id = gateway_data.get("order_id")
        payment.gateway_response = gateway_data
        
        self.db.add(payment)
        await self.db.flush()
        
        # Log payment creation
        await self._log_payment_event(
            payment.id,
            "PAYMENT_CREATED",
            None,
            PaymentStatus.PENDING.value,
            {"gateway": request.payment_gateway.value, "gateway_order_id": payment.gateway_order_id}
        )
        
        return await self._format_payment_response(payment, gateway_data)
    
    async def _create_razorpay_order(self, payment: Payment) -> Dict[str, Any]:
        """Create order in Razorpay (mock implementation for now)"""
        # In production, integrate with actual Razorpay SDK
        # import razorpay
        # client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        # order = client.order.create({
        #     'amount': int(payment.amount * 100),  # Amount in paise
        #     'currency': payment.currency,
        #     'receipt': str(payment.id),
        #     'notes': {'order_id': str(payment.order_id)}
        # })
        
        # Mock response
        mock_order_id = f"order_mock_{uuid.uuid4().hex[:16]}"
        return {
            "order_id": mock_order_id,
            "amount": float(payment.amount),
            "currency": payment.currency,
            "status": "created",
            "razorpay_key_id": settings.RAZORPAY_KEY_ID or "rzp_test_mock_key",
        }
    
    async def _create_cashfree_order(self, payment: Payment) -> Dict[str, Any]:
        """Create order in Cashfree (mock implementation for now)"""
        # In production, integrate with actual Cashfree SDK
        mock_order_id = f"cf_order_mock_{uuid.uuid4().hex[:16]}"
        mock_session_id = f"session_mock_{uuid.uuid4().hex[:16]}"
        return {
            "order_id": mock_order_id,
            "session_id": mock_session_id,
            "amount": float(payment.amount),
            "currency": payment.currency,
            "status": "ACTIVE",
        }
    
    async def verify_razorpay_payment(
        self,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
    ) -> Payment:
        """Verify Razorpay payment signature and update payment status"""
        # Find payment by gateway order ID
        payment = await self.get_payment_by_gateway_order(razorpay_order_id)
        if not payment:
            raise ValueError(f"Payment not found for order {razorpay_order_id}")
        
        # Verify signature
        is_valid = self._verify_razorpay_signature(
            razorpay_order_id,
            razorpay_payment_id,
            razorpay_signature
        )
        
        if not is_valid:
            # Log failed verification
            await self._log_payment_event(
                payment.id,
                "SIGNATURE_VERIFICATION_FAILED",
                payment.status.value,
                PaymentStatus.FAILED.value,
                {"razorpay_payment_id": razorpay_payment_id, "reason": "Invalid signature"}
            )
            payment.status = PaymentStatus.FAILED
            await self.db.flush()
            raise ValueError("Invalid payment signature")
        
        # Update payment status
        old_status = payment.status
        payment.gateway_payment_id = razorpay_payment_id
        payment.gateway_signature = razorpay_signature
        payment.status = PaymentStatus.SUCCESS
        payment.completed_at = datetime.now(UTC)
        payment.webhook_verified = True
        
        await self.db.flush()
        
        # Log successful payment
        await self._log_payment_event(
            payment.id,
            "PAYMENT_SUCCESS",
            old_status.value,
            PaymentStatus.SUCCESS.value,
            {"razorpay_payment_id": razorpay_payment_id}
        )
        
        # Update order service
        await self._update_order_payment_status(payment.order_id, "PAID")
        
        return payment
    
    def _verify_razorpay_signature(
        self,
        order_id: str,
        payment_id: str,
        signature: str
    ) -> bool:
        """Verify Razorpay webhook signature"""
        if not settings.RAZORPAY_KEY_SECRET:
            logger.warning("Razorpay key secret not configured, skipping signature verification")
            return True  # Skip verification in development
        
        message = f"{order_id}|{payment_id}"
        expected_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    async def handle_razorpay_webhook(self, payload: Dict[str, Any], signature: str) -> None:
        """Handle Razorpay webhook event"""
        # Verify webhook signature
        if settings.RAZORPAY_WEBHOOK_SECRET:
            # In production, verify webhook signature
            pass
        
        event = payload.get("event")
        payment_data = payload.get("payload", {}).get("payment", {}).get("entity", {})
        
        if event == "payment.captured":
            # Payment successful
            order_id = payment_data.get("order_id")
            payment_id = payment_data.get("id")
            
            payment = await self.get_payment_by_gateway_order(order_id)
            if payment:
                old_status = payment.status
                payment.gateway_payment_id = payment_id
                payment.status = PaymentStatus.SUCCESS
                payment.completed_at = datetime.now(UTC)
                payment.webhook_verified = True
                
                if not payment.webhook_attempts:
                    payment.webhook_attempts = []
                payment.webhook_attempts.append({
                    "event": event,
                    "timestamp": datetime.now(UTC).isoformat(),
                    "status": "SUCCESS"
                })
                
                await self.db.flush()
                
                await self._log_payment_event(
                    payment.id,
                    "WEBHOOK_PAYMENT_CAPTURED",
                    old_status.value,
                    PaymentStatus.SUCCESS.value,
                    {"payment_id": payment_id}
                )
                
                await self._update_order_payment_status(payment.order_id, "PAID")
        
        elif event == "payment.failed":
            order_id = payment_data.get("order_id")
            payment = await self.get_payment_by_gateway_order(order_id)
            if payment:
                old_status = payment.status
                payment.status = PaymentStatus.FAILED
                payment.gateway_response = payment_data
                
                if not payment.webhook_attempts:
                    payment.webhook_attempts = []
                payment.webhook_attempts.append({
                    "event": event,
                    "timestamp": datetime.now(UTC).isoformat(),
                    "status": "FAILED",
                    "error": payment_data.get("error_description")
                })
                
                await self.db.flush()
                
                await self._log_payment_event(
                    payment.id,
                    "WEBHOOK_PAYMENT_FAILED",
                    old_status.value,
                    PaymentStatus.FAILED.value,
                    {"error": payment_data.get("error_description")}
                )
    
    async def initiate_refund(self, refund_request: RefundRequest) -> Payment:
        """Initiate refund for a payment"""
        payment = await self.get_payment(refund_request.payment_id)
        if not payment:
            raise ValueError(f"Payment {refund_request.payment_id} not found")
        
        if payment.status != PaymentStatus.SUCCESS:
            raise ValueError(f"Cannot refund payment with status {payment.status}")
        
        # Determine refund amount
        refund_amount = refund_request.amount or payment.amount
        if refund_amount > (payment.amount - payment.refund_amount):
            raise ValueError("Refund amount exceeds available amount")
        
        old_status = payment.status
        payment.status = PaymentStatus.REFUND_PENDING
        payment.refund_amount = (payment.refund_amount or 0) + refund_amount
        payment.refund_reason = refund_request.reason
        payment.refund_initiated_at = datetime.now(UTC)
        
        await self.db.flush()
        
        await self._log_payment_event(
            payment.id,
            "REFUND_INITIATED",
            old_status.value,
            PaymentStatus.REFUND_PENDING.value,
            {"refund_amount": float(refund_amount), "reason": refund_request.reason}
        )
        
        # In production, call gateway refund API
        # For now, mark as refunded immediately
        payment.status = PaymentStatus.REFUNDED
        payment.refund_completed_at = datetime.now(UTC)
        await self.db.flush()
        
        # Update order service
        await self._update_order_payment_status(payment.order_id, "REFUNDED")
        
        return payment
    
    async def get_payment(self, payment_id: uuid.UUID) -> Optional[Payment]:
        """Get payment by ID"""
        result = await self.db.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        return result.scalar_one_or_none()
    
    async def get_payment_by_order(self, order_id: uuid.UUID) -> Optional[Payment]:
        """Get payment by order ID"""
        result = await self.db.execute(
            select(Payment).where(Payment.order_id == order_id)
        )
        return result.scalar_one_or_none()
    
    async def get_payment_by_gateway_order(self, gateway_order_id: str) -> Optional[Payment]:
        """Get payment by gateway order ID"""
        result = await self.db.execute(
            select(Payment).where(Payment.gateway_order_id == gateway_order_id)
        )
        return result.scalar_one_or_none()
    
    async def list_payments(
        self,
        customer_id: Optional[uuid.UUID] = None,
        status: Optional[PaymentStatus] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Payment]:
        """List payments with filters"""
        query = select(Payment).order_by(Payment.created_at.desc())
        
        if customer_id:
            query = query.where(Payment.customer_id == customer_id)
        if status:
            query = query.where(Payment.status == status)
        
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_payment_logs(self, payment_id: uuid.UUID) -> List[PaymentLog]:
        """Get payment activity logs"""
        result = await self.db.execute(
            select(PaymentLog)
            .where(PaymentLog.payment_id == payment_id)
            .order_by(PaymentLog.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def _log_payment_event(
        self,
        payment_id: uuid.UUID,
        event_type: str,
        status_from: Optional[str],
        status_to: Optional[str],
        event_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        triggered_by: str = "SYSTEM",
    ):
        """Log payment event"""
        log = PaymentLog(
            id=uuid.uuid4(),
            payment_id=payment_id,
            event_type=event_type,
            status_from=status_from,
            status_to=status_to,
            event_data=event_data,
            error_message=error_message,
            triggered_by=triggered_by,
        )
        self.db.add(log)
        await self.db.flush()
    
    async def _format_payment_response(
        self,
        payment: Payment,
        gateway_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Format payment response with gateway-specific data"""
        response = {
            "payment_id": payment.id,
            "gateway_order_id": payment.gateway_order_id,
            "amount": float(payment.amount),
            "currency": payment.currency,
            "status": payment.status.value,
        }
        
        if gateway_data:
            if payment.payment_gateway == PaymentGateway.RAZORPAY:
                response["razorpay_key_id"] = gateway_data.get("razorpay_key_id")
                response["payment_link"] = f"https://razorpay.com/checkout/{payment.gateway_order_id}"
            elif payment.payment_gateway == PaymentGateway.CASHFREE:
                response["cashfree_session_id"] = gateway_data.get("session_id")
                response["payment_link"] = f"https://cashfree.com/checkout/{gateway_data.get('session_id')}"
        
        return response
    
    async def _update_order_payment_status(self, order_id: uuid.UUID, payment_status: str):
        """Update order payment status via Order Service API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{settings.ORDER_SERVICE_URL}/v1/orders/{order_id}/payment-status",
                    json={"payment_status": payment_status},
                    timeout=10.0
                )
                if response.status_code != 200:
                    logger.error(f"Failed to update order payment status: {response.text}")
        except Exception as e:
            logger.error(f"Error updating order payment status: {e}")
