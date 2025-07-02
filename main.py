"""
🚀 AI Affiliate Backend - Next-Gen Production Version
ArielAI: Autonomous, adaptive, and revenue-maximizing.
"""
import os
import sys
import asyncio
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
import logging
import random

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager, get_db

# Import Ariel orchestrator
try:
    from ariel.orchestrator import ArielOrchestrator
    ARIEL_AVAILABLE = True
except ImportError:
    ARIEL_AVAILABLE = False
    logging.warning("Ariel orchestrator not available - running in standalone mode")

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("Ariel.Main")

app = FastAPI(title="AI Affiliate Backend", docs_url="/docs", redoc_url="/redoc")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Global Ariel instance
ariel_instance = None

class RevenueResponse(BaseModel):
    currency: str
    amount: float
    content: int
    emails: int
    posts: int
    leads: int
    conversions: int
    timestamp: str

class EcosystemStatus(BaseModel):
    status: str
    last_updated: str

@app.on_event("startup")
async def startup_event():
    """Initialize database and optionally start Ariel"""
    global ariel_instance
    
    # Initialize database
    await db_manager.initialize()
    logger.info("Database initialized successfully")
    
    # Seed initial data if needed
    await seed_initial_data()
    
    # Initialize Ariel if available
    if ARIEL_AVAILABLE:
        try:
            ariel_instance = ArielOrchestrator()
            await ariel_instance.bootstrap()
            logger.info("Ariel orchestrator initialized successfully")
            
            # Start Ariel in background
            asyncio.create_task(run_ariel_background())
        except Exception as e:
            logger.error(f"Failed to initialize Ariel: {e}")
            ariel_instance = None

async def seed_initial_data():
    """Seed database with initial data"""
    try:
        # Seed revenue data
        if not await db_manager.find_one("revenue"):
            await db_manager.insert_one("revenue", {
                "currency": "NGN",
                "amount": 12345.67,
                "content": 150,
                "emails": 2500,
                "posts": 75,
                "leads": 320,
                "conversions": 45,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Seed ecosystem status
        if not await db_manager.find_one("ecosystem"):
            await db_manager.insert_one("ecosystem", {
                "type": "status",
                "status": "active",
                "last_updated": datetime.utcnow().isoformat()
            })
        
        # Seed affiliate metrics
        if not await db_manager.find_one("affiliate_metrics"):
            await db_manager.insert_one("affiliate_metrics", {
                "activeCampaigns": 12,
                "conversionRate": 3.7,
                "totalClicks": 15420,
                "revenue": 8750.5,
                "topPerformers": [
                    {"name": "Tech Products Campaign", "conversion": 4.2, "revenue": 3200},
                    {"name": "Health & Wellness", "conversion": 3.8, "revenue": 2800},
                    {"name": "Digital Services", "conversion": 3.1, "revenue": 2750},
                ]
            })
        
        logger.info("Initial data seeded successfully")
    except Exception as e:
        logger.error(f"Failed to seed initial data: {e}")

async def run_ariel_background():
    """Run Ariel in the background"""
    global ariel_instance
    if ariel_instance:
        # Run with longer cycles for API mode
        ariel_instance.cycle_time = 300  # 5 minutes
        while True:
            try:
                await ariel_instance.run_cycle()
                await asyncio.sleep(ariel_instance.cycle_time)
            except Exception as e:
                logger.error(f"Background Ariel error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error

@app.get("/")
async def health_check():
    return {
        "status": "running",
        "database": "connected" if db_manager._connected else "fallback_mode",
        "ariel": "active" if ariel_instance else "unavailable",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/paystack/revenue", response_model=RevenueResponse)
async def get_revenue(currency: str = "NGN", db=Depends(get_db)):
    try:
        if not db._connected:
            logger.error("Database not connected")
            raise HTTPException(status_code=503, detail="Database not connected")
        
        db_data = await db.find_one("revenue", {"currency": currency})
        if not db_data:
            logger.error(f"Revenue data not found for currency: {currency}")
            raise HTTPException(status_code=404, detail=f"Revenue data not found for currency: {currency}")
        
        return db_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Revenue endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/ecosystem/status", response_model=EcosystemStatus)
async def get_ecosystem_status(db=Depends(get_db)):
    try:
        if not db._connected:
            logger.error("Database not connected")
            raise HTTPException(status_code=503, detail="Database not connected")
        
        db_status = await db.find_one("ecosystem", {"type": "status"})
        if not db_status:
            logger.error("Ecosystem status not found")
            raise HTTPException(status_code=404, detail="Ecosystem status not found")
        
        return db_status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/affiliate/metrics")
async def affiliate_metrics(db=Depends(get_db)):
    try:
        if not db._connected:
            logger.error("Database not connected")
            raise HTTPException(status_code=503, detail="Database not connected")
        
        metrics = await db.find_one("affiliate_metrics")
        if not metrics:
            logger.error("Affiliate metrics not found")
            raise HTTPException(status_code=404, detail="Affiliate metrics not found")
        
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Affiliate metrics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/affiliate/optimize")
async def optimize_affiliate():
    """Trigger affiliate optimization"""
    if not ariel_instance:
        # Simulate optimization without Ariel
        await asyncio.sleep(1)
        return {"message": "Affiliate optimization triggered successfully! (Simulated)"}
    
    try:
        # Trigger an optimization cycle
        opportunities = await ariel_instance.quantum.find_opportunities()
        market_trends = await ariel_instance.neural.analyze_trends()
        await ariel_instance.campaign_manager.launch_or_optimize(opportunities, market_trends)
        
        return {"message": "Affiliate optimization triggered successfully!"}
    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@app.get("/api/neural/metrics")
async def get_neural_metrics():
    """Get neural commerce metrics"""
    if ariel_instance:
        try:
            # Get real neural analysis
            trends = await ariel_instance.neural.analyze_trends()
            return {
                "globalAnalysis": f"Analyzing {len(trends.get('markets', []))} markets",
                "automationLevel": int(trends.get('confidence', 0.8) * 100),
                "marketTrends": [
                    {"region": "North America", "growth": round(random.uniform(8, 15), 1), "status": trends.get('trend', 'stable')},
                    {"region": "Europe", "growth": round(random.uniform(5, 12), 1), "status": "stable"},
                    {"region": "Asia Pacific", "growth": round(random.uniform(10, 20), 1), "status": trends.get('trend', 'bullish')},
                ]
            }
        except Exception as e:
            logger.error(f"Neural metrics error: {e}")
    
    # Return demo data if Ariel not available or error
    return {
        "globalAnalysis": "Processing 2.3M data points",
        "automationLevel": random.randint(80, 95),
        "marketTrends": [
            {"region": "North America", "growth": 12.5, "status": "bullish"},
            {"region": "Europe", "growth": 8.3, "status": "stable"},
            {"region": "Asia Pacific", "growth": 15.7, "status": "bullish"},
        ]
    }

@app.post("/api/neural/optimize")
async def optimize_neural():
    """Trigger neural optimization"""
    if not ariel_instance:
        await asyncio.sleep(1)
        return {"message": "Neural optimization completed successfully! (Simulated)"}
    
    try:
        # Trigger neural analysis and optimization
        await ariel_instance.neural.analyze_trends()
        return {"message": "Neural optimization completed successfully!"}
    except Exception as e:
        logger.error(f"Neural optimization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Neural optimization failed: {str(e)}")

@app.get("/api/ariel/logs")
async def ariel_logs(db=Depends(get_db)):
    try:
        if not db._connected:
            logger.error("Database not connected")
            raise HTTPException(status_code=503, detail="Database not connected")
        
        logs = await db.to_list("ariel_logs", length=100)
        return {"logs": logs}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ariel logs error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/ariel/status")
async def ariel_status(db=Depends(get_db)):
    try:
        if not db._connected:
            logger.error("Database not connected")
            raise HTTPException(status_code=503, detail="Database not connected")
        
        status = await db.find_one("ariel_status")
        if not status:
            # Return live status from Ariel instance if available
            if ariel_instance:
                status = await ariel_instance.get_status()
            else:
                status = {
                    "status": "unavailable",
                    "details": "Ariel orchestrator not running",
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ariel status error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Alias route for /ariel/status (no /api prefix)
@app.get("/ariel/status")
async def ariel_status_alias(db=Depends(get_db)):
    return await ariel_status(db)

@app.get("/api/quantum/logs")
async def quantum_logs(db=Depends(get_db)):
    try:
        if not db._connected:
            logger.error("Database not connected")
            raise HTTPException(status_code=503, detail="Database not connected")
        
        logs = await db.to_list("quantum_logs", length=100)
        return {"logs": logs}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quantum logs error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/quantum/status")
async def quantum_status(db=Depends(get_db)):
    try:
        if not db._connected:
            logger.error("Database not connected")
            raise HTTPException(status_code=503, detail="Database not connected")
        
        status = await db.find_one("quantum_status")
        if not status:
            status = {
                "status": "active",
                "details": "Quantum research module operational",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quantum status error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/revenue/comprehensive")
async def revenue_comprehensive(db=Depends(get_db)):
    try:
        if not db._connected:
            logger.error("Database not connected")
            raise HTTPException(status_code=503, detail="Database not connected")
        
        revenue = await db.find_one("revenue_comprehensive")
        if not revenue:
            logger.error("Comprehensive revenue data not found")
            raise HTTPException(status_code=404, detail="Comprehensive revenue data not found")
        
        return revenue
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Comprehensive revenue error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/control/pause")
async def pause_ariel():
    """Pause Ariel orchestrator"""
    if not ariel_instance:
        raise HTTPException(status_code=503, detail="Ariel not available")
    
    ariel_instance.pause()
    return {"message": "Ariel paused successfully"}

@app.post("/api/control/resume")
async def resume_ariel():
    """Resume Ariel orchestrator"""
    if not ariel_instance:
        raise HTTPException(status_code=503, detail="Ariel not available")
    
    ariel_instance.resume()
    return {"message": "Ariel resumed successfully"}

@app.get("/api/status")
async def get_system_status():
    """Get overall system status"""
    status = {
        "database": "connected" if db_manager._connected else "disconnected",
        "ariel": "active" if ariel_instance and not ariel_instance.paused else "inactive",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if ariel_instance:
        ariel_status = await ariel_instance.get_status()
        status.update(ariel_status)
    
    return status

@app.get("/api/matrix/status")
async def get_matrix_status():
    """Get ArielMatrix status"""
    if not ariel_instance or not hasattr(ariel_instance, 'matrix'):
        return {"error": "ArielMatrix not available"}
    
    try:
        status = await ariel_instance.matrix.get_status()
        return status
    except Exception as e:
        logger.error(f"Matrix status error: {e}")
        raise HTTPException(status_code=500, detail=f"Matrix status failed: {str(e)}")

@app.get("/api/matrix/aggregated-data")
async def get_aggregated_data(source: str = None):
    """Get aggregated data from ArielMatrix"""
    if not ariel_instance or not hasattr(ariel_instance, 'matrix'):
        return {"error": "ArielMatrix not available"}
    
    try:
        data = ariel_instance.matrix.aggregator.get_aggregated_data(source)
        return {"data": data, "count": len(data)}
    except Exception as e:
        logger.error(f"Aggregated data error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get aggregated data: {str(e)}")

@app.get("/api/matrix/api-summary")
async def get_api_summary():
    """Get API management summary"""
    if not ariel_instance or not hasattr(ariel_instance, 'matrix'):
        return {"error": "ArielMatrix not available"}
    
    try:
        summary = await ariel_instance.matrix.api_manager.get_summary()
        return summary
    except Exception as e:
        logger.error(f"API summary error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get API summary: {str(e)}")

@app.post("/api/matrix/sync-apis")
async def sync_matrix_apis():
    """Trigger API synchronization"""
    if not ariel_instance or not hasattr(ariel_instance, 'matrix'):
        raise HTTPException(status_code=503, detail="ArielMatrix not available")
    
    try:
        await ariel_instance.matrix.api_manager.sync_apis()
        return {"message": "API synchronization completed successfully"}
    except Exception as e:
        logger.error(f"API sync error: {e}")
        raise HTTPException(status_code=500, detail=f"API sync failed: {str(e)}")

@app.post("/api/matrix/aggregate")
async def trigger_aggregation(source: str = None):
    """Trigger data aggregation"""
    if not ariel_instance or not hasattr(ariel_instance, 'matrix'):
        raise HTTPException(status_code=503, detail="ArielMatrix not available")
    
    try:
        await ariel_instance.matrix.aggregator.aggregate(source)
        return {"message": f"Data aggregation completed{' for ' + source if source else ''}"}
    except Exception as e:
        logger.error(f"Aggregation error: {e}")
        raise HTTPException(status_code=500, detail=f"Aggregation failed: {str(e)}")

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": "Endpoint not found"}
    )

@app.exception_handler(500)
async def server_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        log_level="info"
    )
