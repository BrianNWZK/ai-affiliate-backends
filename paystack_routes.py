import os
import hmac
import hashlib
import json
from fastapi import APIRouter, HTTPException, Request, Depends, status
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import httpx
import redis
from pydantic import BaseModel
from .paystack import PaystackService, TransactionStatus  # Import from your improved paystack.py

router = APIRouter(prefix="/paystack", tags=["Paystack Services"])

# Initialize services
paystack_service = PaystackService()
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"), decode_responses=True)

# ==================== MODELS ====================
class RevenueResponse(BaseModel):
    total_revenue: float
    currency: str
    transactions_count: int
    is_cached: bool
    last_updated: str
    is_stale: Optional[bool] = False

class WebhookEvent(BaseModel):
    event: str
    data: Dict

# ==================== UTILITIES ====================
async def verify_webhook(request: Request):
    signature = request.headers.get("x-paystack-signature")
    body = await request.body()
    if not paystack_service.verify_webhook_signature(body, signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature"
        )
    return json.loads(body)

# ==================== API ENDPOINTS ====================
@router.get("/revenue", response_model=RevenueResponse)
async def get_real_revenue():
    """Enhanced revenue endpoint with smart caching"""
    cache_key = "paystack:revenue:v2"
    fallback_key = f"{cache_key}:fallback"
    try:
        # Try cache first
        cached = redis_client.get(cache_key)
        if cached:
            cached_data = json.loads(cached)
            cached_data["is_cached"] = True
            return cached_data

        # Fetch fresh data
        transactions = await paystack_service.fetch_successful_transactions()
        total = sum(txn["amount"] for txn in transactions) / 100  # kobo to NGN

        response = RevenueResponse(
            total_revenue=total,
            currency="NGN",
            transactions_count=len(transactions),
            is_cached=False,
            last_updated=datetime.now().isoformat()
        )

        # Cache with expiry
        redis_client.setex(
            cache_key,
            int(timedelta(minutes=15).total_seconds()),
            json.dumps(response.dict())
        )
        # Save fallback as well
        redis_client.set(
            fallback_key,
            json.dumps(response.dict())
        )
        return response

    except Exception as e:
        # Fallback to stale cache if available
        stale_cache = redis_client.get(fallback_key)
        if stale_cache:
            data = json.loads(stale_cache)
            data["is_cached"] = True
            data["is_stale"] = True
            return data
        raise HTTPException(500, f"Failed to fetch revenue data: {e}")

@router.post("/webhook")
async def handle_webhook(request: Request):
    """Secure webhook processing with event handling"""
    try:
        event = await verify_webhook(request)
        # Process different event types
        if event["event"] == "charge.success":
            await process_successful_charge(event["data"])
        elif event["event"] == "transfer.success":
            await process_transfer(event["data"])
        return {"status": "processed"}
    except Exception as e:
        # Dead letter queue for failed webhooks
        body = await request.body()
        redis_client.rpush("paystack:webhook:dlq", json.dumps({
            "payload": body.decode() if isinstance(body, bytes) else str(body),
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }))
        raise HTTPException(400, f"Webhook processing failed: {e}")

# ==================== BUSINESS LOGIC ====================
async def process_successful_charge(charge_data: Dict):
    """Handle successful payments"""
    amount = charge_data["amount"] / 100
    redis_client.incrbyfloat("paystack:revenue:current", amount)

    # Update user balance
    user_id = charge_data.get("metadata", {}).get("user_id")
    if user_id:
        redis_client.hincrbyfloat(f"user:{user_id}", "balance", amount * 0.85)  # 85% payout

async def process_transfer(transfer_data: Dict):
    """Handle completed payouts"""
    reference = transfer_data.get("reference")
    if reference:
        redis_client.sadd("paystack:payouts:processed", reference)
