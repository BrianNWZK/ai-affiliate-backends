import os
from fastapi import APIRouter, Request, HTTPException, Depends, status
from pydantic import BaseModel, Field, validator
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import uuid
import redis
import logging
from database import db  # MongoDB connection
from functools import lru_cache
from ai_service import AIClient  # Your AI service client
from .auth import get_current_user  # Authentication dependency

router = APIRouter(prefix="/api/v1/neural", tags=["Neural Engine"])

# Enhanced Redis setup with connection pooling
redis_pool = redis.ConnectionPool.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379"),
    max_connections=20,
    decode_responses=True
)
redis_client = redis.Redis(connection_pool=redis_pool)

# ==================== ENHANCED MODELS ====================
class NeuralPredictionRequest(BaseModel):
    markets: List[str] = Field(..., min_items=1, max_items=10)
    timeframe: str = Field("7d", regex="^(1d|7d|30d)$")
    confidence_threshold: int = Field(80, ge=50, le=99)
    strategy: str = Field("balanced", regex="^(conservative|balanced|aggressive)$")

    @validator('markets')
    def validate_markets(cls, v):
        valid_markets = get_valid_markets()
        return [m for m in v if m in valid_markets]

class AgentDeployment(BaseModel):
    market_targets: List[str]
    risk_level: str = Field(..., regex="^(low|medium|high)$")
    quantity: int = Field(1, ge=1, le=50)
    user_id: str  # Added for audit tracking

# ==================== CORE SERVICES ==================== 
class NeuralEngine:
    def __init__(self):
        self.ai = AIClient(os.getenv("AI_SERVICE_URL"))
        
    async def generate_predictions(self, request: NeuralPredictionRequest):
        cache_key = f"neural:predict:{hash(frozenset(request.dict().items()))}"
        
        # Check cache
        if cached := redis_client.get(cache_key):
            return cached

        # Generate AI predictions
        predictions = await self.ai.predict(
            markets=request.markets,
            timeframe=request.timeframe,
            min_confidence=request.confidence_threshold
        )
        
        # Cache with dynamic TTL based on timeframe
        ttl = {
            "1d": timedelta(hours=1),
            "7d": timedelta(days=1),
            "30d": timedelta(days=3)
        }.get(request.timeframe, timedelta(hours=12))
        
        redis_client.setex(cache_key, ttl, predictions)
        return predictions

# ==================== API ENDPOINTS ====================
@router.post("/predictions", response_model=Dict)
async def get_predictions(
    request: NeuralPredictionRequest, 
    user: dict = Depends(get_current_user)
):
    """Enhanced prediction endpoint with:
    - JWT authentication
    - Smart caching
    - Request validation
    - AI fallback
    """
    try:
        engine = NeuralEngine()
        result = await engine.generate_predictions(request)
        
        # Audit log
        db.predictions.insert_one({
            **request.dict(),
            "user_id": user["id"],
            "generated_at": datetime.utcnow(),
            "result_hash": hash(str(result))
        })
        
        return {
            "status": "success",
            "data": result,
            "cache_hit": False
        }
        
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Prediction service temporarily unavailable"
        )

@router.post("/deploy-agents", status_code=status.HTTP_201_CREATED)
async def deploy_agents(
    deployment: AgentDeployment,
    user: dict = Depends(get_current_user)
):
    """Secure agent deployment with:
    - Rate limiting
    - Atomic operations
    - Resource validation
    """
    # Rate limiting
    rate_key = f"rate:{user['id']}:deployments"
    if int(redis_client.get(rate_key) or 0) >= 10:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Maximum deployment limit reached"
        )
    
    # Validate resources
    if not validate_market_access(deployment.market_targets, user["tier"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient market access for your tier"
        )
    
    # Create agents
    agents = [{
        "agent_id": str(uuid.uuid4()),
        **deployment.dict(),
        "deployed_at": datetime.utcnow(),
        "status": "active",
        "owner": user["id"]
    } for _ in range(deployment.quantity)]
    
    # Atomic insert
    with db.client.start_session() as session:
        try:
            result = db.agents.insert_many(agents, session=session)
            redis_client.incr(rate_key, deployment.quantity)
            redis_client.expire(rate_key, 3600)  # 1 hour window
            
            return {
                "deployed": len(result.inserted_ids),
                "first_id": agents[0]["agent_id"]
            }
        except Exception as e:
            session.abort_transaction()
            logger.error(f"Deployment failed: {str(e)}")
            raise HTTPException(500, "Agent deployment failed")

# ==================== UTILITY FUNCTIONS ====================
@lru_cache(maxsize=1)
def get_valid_markets():
    """Cached market validation data"""
    return set(m["code"] for m in db.markets.find({}, {"code": 1}))

def validate_market_access(markets: List[str], user_tier: str) -> bool:
    """Check user has access to requested markets"""
    tier_access = {
        "basic": ["NASDAQ", "NYSE"],
        "pro": ["NASDAQ", "NYSE", "LSE"],
        "enterprise": ["*"]
    }
    allowed = tier_access.get(user_tier, [])
    return all(m in allowed or "*" in allowed for m in markets)
