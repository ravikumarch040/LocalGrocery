"""Payment API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.payment_service import PaymentService
from app.api.v1.schemas.payments import (
    PaymentInitiateRequest,
    PaymentInitiateResponse,
    PaymentResponse,
    PaymentVerifyRequest,
    RefundRequest,
    StandardResponse,
    PaymentLogResponse,
    RazorpayWebhookPayload,
)
from typing import List, Optional
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/initiate", response_model=StandardResponse)
async def initiate_payment(
    request: PaymentInitiateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Initiate a new payment
    
    Creates a payment record and initiates payment with the selected gateway.
    Returns payment details including gateway order ID and payment link.
    """
    try:
        service = PaymentService(db)
        payment_data = await service.initiate_payment(request)
        
        return StandardResponse(
            success=True,
            message="Payment initiated successfully",
            data=payment_data
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error initiating payment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to initiate payment")


@router.post("/verify", response_model=StandardResponse)
async def verify_payment(
    request: PaymentVerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify Razorpay payment
    
    Verifies payment signature and updates payment status.
    Called after customer completes payment on Razorpay checkout.
    """
    try:
        service = PaymentService(db)
        payment = await service.verify_razorpay_payment(
            request.razorpay_order_id,
            request.razorpay_payment_id,
            request.razorpay_signature
        )
        
        return StandardResponse(
            success=True,
            message="Payment verified successfully",
            data=PaymentResponse.model_validate(payment)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error verifying payment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to verify payment")


@router.get("/{payment_id}", response_model=StandardResponse)
async def get_payment(
    payment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get payment details by ID"""
    try:
        service = PaymentService(db)
        payment = await service.get_payment(payment_id)
        
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        return StandardResponse(
            success=True,
            message="Payment retrieved successfully",
            data=PaymentResponse.model_validate(payment)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving payment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve payment")


@router.get("/order/{order_id}", response_model=StandardResponse)
async def get_payment_by_order(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get payment by order ID"""
    try:
        service = PaymentService(db)
        payment = await service.get_payment_by_order(order_id)
        
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found for order")
        
        return StandardResponse(
            success=True,
            message="Payment retrieved successfully",
            data=PaymentResponse.model_validate(payment)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving payment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve payment")


@router.get("", response_model=StandardResponse)
async def list_payments(
    customer_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """List payments with filters"""
    try:
        service = PaymentService(db)
        
        # Convert status string to enum if provided
        status_enum = None
        if status:
            from app.models import PaymentStatus
            status_enum = PaymentStatus(status)
        
        payments = await service.list_payments(
            customer_id=customer_id,
            status=status_enum,
            skip=skip,
            limit=limit
        )
        
        return StandardResponse(
            success=True,
            message=f"Retrieved {len(payments)} payments",
            data=[PaymentResponse.model_validate(p) for p in payments]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing payments: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list payments")


@router.post("/refund", response_model=StandardResponse)
async def initiate_refund(
    request: RefundRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Initiate refund for a payment
    
    Creates a refund request for full or partial refund.
    """
    try:
        service = PaymentService(db)
        payment = await service.initiate_refund(request)
        
        return StandardResponse(
            success=True,
            message="Refund initiated successfully",
            data=PaymentResponse.model_validate(payment)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error initiating refund: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to initiate refund")


@router.get("/{payment_id}/logs", response_model=StandardResponse)
async def get_payment_logs(
    payment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get payment activity logs"""
    try:
        service = PaymentService(db)
        logs = await service.get_payment_logs(payment_id)
        
        return StandardResponse(
            success=True,
            message=f"Retrieved {len(logs)} logs",
            data=[PaymentLogResponse.model_validate(log) for log in logs]
        )
    except Exception as e:
        logger.error(f"Error retrieving payment logs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve payment logs")


# Webhook endpoints
@router.post("/webhooks/razorpay", response_model=StandardResponse)
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Razorpay webhook events
    
    Receives payment status updates from Razorpay.
    Signature verification ensures authenticity.
    """
    try:
        payload = await request.json()
        
        service = PaymentService(db)
        await service.handle_razorpay_webhook(payload, x_razorpay_signature or "")
        
        return StandardResponse(
            success=True,
            message="Webhook processed successfully",
            data={"event": payload.get("event")}
        )
    except Exception as e:
        logger.error(f"Error processing Razorpay webhook: {e}", exc_info=True)
        # Return 200 to prevent webhook retries for invalid payloads
        return StandardResponse(
            success=False,
            message="Webhook processing failed",
            error={"detail": str(e)}
        )


@router.post("/webhooks/cashfree", response_model=StandardResponse)
async def cashfree_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Cashfree webhook events
    
    Receives payment status updates from Cashfree.
    """
    try:
        payload = await request.json()
        
        # In production, implement Cashfree webhook handling
        logger.info(f"Received Cashfree webhook: {payload}")
        
        return StandardResponse(
            success=True,
            message="Webhook received",
            data={"type": payload.get("type")}
        )
    except Exception as e:
        logger.error(f"Error processing Cashfree webhook: {e}", exc_info=True)
        return StandardResponse(
            success=False,
            message="Webhook processing failed",
            error={"detail": str(e)}
        )
