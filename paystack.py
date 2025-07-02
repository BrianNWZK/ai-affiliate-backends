import os
import hmac
import hashlib
import httpx
from fastapi import APIRouter, HTTPException, Request, status, BackgroundTasks, Depends
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum
from database import get_db

router = APIRouter(prefix="/paystack", tags=["Paystack Payment Gateway"])

# Constants
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
PAYSTACK_BASE_URL = "https://api.paystack.co"
WEBHOOK_SECRET = os.getenv("PAYSTACK_WEBHOOK_SECRET")

# ------------------- Enhanced Models ------------------- #

class TransactionStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REVERSED = "reversed"
    VERIFIED = "verified"

class EnhancedCheckoutRequest(BaseModel):
    email: EmailStr
    amount: float = Field(..., gt=0)
    currency: str = Field(default="NGN", regex="^[A-Z]{3}$")
    metadata: Dict = Field(default={}, description="Additional transaction context")
    callback_url: Optional[str]
    channels: List[str] = Field(
        default=["card", "bank", "ussd"],
        description="Enabled payment channels"
    )
    reference: Optional[str] = Field(
        max_length=50,
        description="Custom transaction reference"
    )

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        return round(v, 2)

class EnhancedCheckoutResponse(BaseModel):
    authorization_url: str
    access_code: str
    reference: str
    expires_at: datetime
    currency: str
    amount: float

class WebhookEvent(str, Enum):
    CHARGE_SUCCESS = "charge.success"
    TRANSFER_SUCCESS = "transfer.success"
    SUBSCRIPTION_CREATE = "subscription.create"

# ------------------- Core Payment Processor ------------------- #

class PaystackProcessor:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=PAYSTACK_BASE_URL)
        self.headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }

    async def initialize_payment(self, request: EnhancedCheckoutRequest) -> dict:
        payload = {
            "email": request.email,
            "amount": int(request.amount * 100),  # Convert to kobo
            "currency": request.currency,
            "metadata": request.metadata,
            "channels": request.channels,
            "callback_url": request.callback_url
        }
        if request.reference:
            payload["reference"] = request.reference

        try:
            response = await self.client.post(
                "/transaction/initialize",
                json=payload,
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            if not data.get("status", False):
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail=data.get("message", "Payment initialization failed")
                )
            return {
                **data["data"],
                "amount": request.amount,
                "currency": request.currency
            }
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Payment gateway timeout"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Payment processing error: {str(e)}"
            )

    async def verify_transaction(self, reference: str) -> dict:
        try:
            response = await self.client.get(
                f"/transaction/verify/{reference}",
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            if not data.get("status", False):
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail="Transaction verification failed"
                )
            return self._normalize_verification_data(data["data"])
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Verification error: {str(e)}"
            )

    def _normalize_verification_data(self, data: dict) -> dict:
        return {
            "status": data["status"],
            "reference": data["reference"],
            "amount": float(data["amount"]) / 100,
            "currency": data["currency"],
            "metadata": data.get("metadata", {}),
            "paid_at": data.get("paid_at"),
            "channel": data.get("channel"),
            "fees": float(data.get("fees", 0)) / 100
        }

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        computed_signature = hmac.new(
            WEBHOOK_SECRET.encode('utf-8'),
            payload,
            digestmod=hashlib.sha512
        ).hexdigest()
        return hmac.compare_digest(computed_signature, signature)

# ------------------- Database Models ------------------- #

async def log_transaction(db, transaction_data: dict):
    if hasattr(db, "db") and db.db:
        await db.db.transactions.insert_one(transaction_data)

async def update_transaction_status(db, reference: str, status: TransactionStatus):
    if hasattr(db, "db") and db.db:
        await db.db.transactions.update_one(
            {"reference": reference},
            {"$set": {"status": status, "updated_at": datetime.utcnow()}}
        )

# ------------------- API Endpoints ------------------- #

@router.post("/checkout", response_model=EnhancedCheckoutResponse)
async def checkout_payment(
    request: EnhancedCheckoutRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_db)
):
    processor = PaystackProcessor()
    try:
        result = await processor.initialize_payment(request)
        background_tasks.add_task(log_transaction, db, {
            **result,
            "status": TransactionStatus.PENDING,
            "user_email": request.email
        })
        return EnhancedCheckoutResponse(**result)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment processing failed: {str(e)}"
        )

@router.get("/verify/{reference}", response_model=dict)
async def verify_payment(
    reference: str,
    background_tasks: BackgroundTasks,
    db=Depends(get_db)
):
    processor = PaystackProcessor()
    try:
        verification = await processor.verify_transaction(reference)
        background_tasks.add_task(
            update_transaction_status,
            db,
            reference,
            TransactionStatus.VERIFIED if verification["status"] == "success" else TransactionStatus.FAILED
        )
        return verification
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}"
        )

@router.post("/webhook")
async def handle_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db=Depends(get_db)
):
    payload = await request.body()
    signature = request.headers.get("x-paystack-signature", "")
    processor = PaystackProcessor()
    if not processor.verify_webhook_signature(payload, signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature"
        )
    event_data = await request.json()
    event_type = event_data.get("event")
    if event_type == WebhookEvent.CHARGE_SUCCESS:
        background_tasks.add_task(
            update_transaction_status,
            db,
            event_data["data"]["reference"],
            TransactionStatus.SUCCESS
        )
    elif event_type == WebhookEvent.TRANSFER_SUCCESS:
        background_tasks.add_task(
            update_transaction_status,
            db,
            event_data["data"]["reference"],
            TransactionStatus.SUCCESS
        )
    return {"status": "webhook_processed"}
